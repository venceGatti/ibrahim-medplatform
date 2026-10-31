use std::io::Write;
use std::net::TcpListener;
use std::process::{Child, Command, Stdio};
use crc32fast::Hasher;
use uuid::Uuid;

use crate::base::models::SidecarHandshakeConfig;
use crate::interfaces::traits::IJobSupervisor;

pub fn allocate_ephemeral_port_and_token() -> Result<SidecarHandshakeConfig, String> {
    // 1. Alloca porta dinamica legandosi a 127.0.0.1:0 e leggendo la porta assegnata dal kernel
    let listener = TcpListener::bind("127.0.0.1:0")
        .map_err(|e| format!("Impossibile allocare socket effimero: {}", e))?;
    let ephemeral_port = listener
        .local_addr()
        .map_err(|e| format!("Impossibile determinare local_addr: {}", e))?
        .port();

    // Rilascia listener prima della continuazione dell'handshake
    drop(listener);

    // 2. Genera token UUIDv4 CSPRNG
    let token = Uuid::new_v4().to_string();

    // 3. Costruisce frame TLV:
    // Magic: 0xCA 0xFE (2B)
    // Port: uint16 Big-Endian (2B)
    // Token Len: uint16 Big-Endian (2B) -> 36 bytes per UUIDv4
    // Token: 36 bytes UTF-8
    // Checksum: CRC-32 (IEEE) dei primi 42 bytes (4B Big-Endian)
    let mut ipc_message_buffer = Vec::with_capacity(46);
    ipc_message_buffer.extend_from_slice(&[0xCA, 0xFE]);
    ipc_message_buffer.extend_from_slice(&ephemeral_port.to_be_bytes());
    let token_bytes = token.as_bytes();
    let token_length = token_bytes.len() as u16;
    ipc_message_buffer.extend_from_slice(&token_length.to_be_bytes());
    ipc_message_buffer.extend_from_slice(token_bytes);

    let mut hasher = Hasher::new();
    hasher.update(&ipc_message_buffer);
    let checksum = hasher.finalize();
    ipc_message_buffer.extend_from_slice(&checksum.to_be_bytes());

    Ok(SidecarHandshakeConfig::new(
        ephemeral_port,
        token,
        ipc_message_buffer,
    ))
}

pub fn inject_token_into_stream<W: Write>(
    stream_writer: &mut W,
    token: &str,
) -> std::io::Result<()> {
    stream_writer.write_all(token.as_bytes())?;
    stream_writer.write_all(b"\n")?;
    stream_writer.flush()?;
    Ok(())
}

pub fn build_sidecar_command_args(
    additional_arguments: &[String],
    ephemeral_port: u16,
) -> Vec<String> {
    let mut ordered_arguments = Vec::with_capacity(additional_arguments.len() + 1);
    for argument in additional_arguments {
        ordered_arguments.push(argument.clone());
    }
    ordered_arguments.push(format!("--port={}", ephemeral_port));
    ordered_arguments
}

pub fn spawn_sidecar_process(
    executable_path: &str,
    additional_arguments: &[String],
    handshake_config: &SidecarHandshakeConfig,
    job_supervisor: Option<&dyn IJobSupervisor>,
) -> Result<Child, String> {
    let mut command_builder = Command::new(executable_path);

    // Argomenti espliciti: additional_arguments (es. -m medclient.sidecar_python.src.main) PRIMA di --port=<port>
    let ordered_args =
        build_sidecar_command_args(additional_arguments, handshake_config.ephemeral_port);
    for argument in &ordered_args {
        command_builder.arg(argument);
    }

    command_builder.env("MEDCLIENT_PARENT_PID", std::process::id().to_string());

    command_builder
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped());

    let mut spawned_process = command_builder
        .spawn()
        .map_err(|e| format!("Avvio processo sidecar fallito: {}", e))?;

    // Iniezione sicura del token effimero sulla prima riga di stdin
    if let Some(mut stdin_pipe) = spawned_process.stdin.take() {
        inject_token_into_stream(&mut stdin_pipe, &handshake_config.token)
            .map_err(|e| format!("Scrittura token su stdin fallita: {}", e))?;
    } else {
        return Err("Pipe stdin non disponibile per il child process".to_string());
    }

    // Incapsulamento immediato nel Win32 Job Object per garantire terminazione sincrona
    if let Some(supervisor) = job_supervisor {
        let process_id = spawned_process.id();
        supervisor
            .assign_process_by_id(process_id)
            .map_err(|e| format!("Assegnazione PID {} a Job Object fallita: {}", process_id, e))?;
    }

    Ok(spawned_process)
}
