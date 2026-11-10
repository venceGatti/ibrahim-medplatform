import React, { useState } from 'react';

export const MAX_MOUNTED_DOM_NODES = 30;

export interface VirtualWindowCalculation {
  readonly startIndex: number;
  readonly endIndex: number;
  readonly mountedCount: number;
  readonly totalHeightPx: number;
  readonly offsetY: number;
}

export function computeVirtualWindowRange(
  totalItemsCount: number,
  viewportHeightPx: number,
  rowHeightPx: number,
  scrollTopPx: number,
  overscanCount = 3
): VirtualWindowCalculation {
  if (totalItemsCount <= 0) {
    return {
      startIndex: 0,
      endIndex: 0,
      mountedCount: 0,
      totalHeightPx: 0,
      offsetY: 0,
    };
  }

  const safeRowHeight = Math.max(24, rowHeightPx);
  const safeViewportHeight = Math.max(safeRowHeight, viewportHeightPx);
  const totalHeightPx = totalItemsCount * safeRowHeight;
  const clampedScrollTop = Math.max(0, Math.min(scrollTopPx, totalHeightPx));

  const rawFirstVisible = Math.floor(clampedScrollTop / safeRowHeight);
  const visibleRows = Math.ceil(safeViewportHeight / safeRowHeight);

  const safeOverscan = Math.max(1, overscanCount);
  const startIndex = Math.max(0, rawFirstVisible - safeOverscan);

  const maxAllowedEnd = Math.min(
    totalItemsCount,
    startIndex + MAX_MOUNTED_DOM_NODES - 1
  );
  const desiredEnd = Math.min(
    totalItemsCount,
    rawFirstVisible + visibleRows + safeOverscan
  );
  const endIndex = Math.min(maxAllowedEnd, desiredEnd);
  const mountedCount = Math.max(0, endIndex - startIndex);

  return {
    startIndex,
    endIndex,
    mountedCount,
    totalHeightPx,
    offsetY: startIndex * safeRowHeight,
  };
}

export interface VirtualBlockWindowProps {
  readonly paragraphs: readonly string[];
  readonly viewportHeightPx?: number;
  readonly rowHeightPx?: number;
  readonly initialScrollTopPx?: number;
  readonly onScrollOffsetChange?: (scrollTopPx: number) => void;
}

const renderInlineMarkdown = (text: string): React.ReactNode[] => {
  const parts = text.split(/(\*\*.*?\*\*|\*.*?\*)/g);
  return parts.map((part, index) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return <strong key={index}>{part.slice(2, -2)}</strong>;
    }
    if (part.startsWith('*') && part.endsWith('*')) {
      return <em key={index}>{part.slice(1, -1)}</em>;
    }
    return <React.Fragment key={index}>{part}</React.Fragment>;
  });
};

export const VirtualBlockWindow: React.FC<VirtualBlockWindowProps> = ({
  paragraphs,
  viewportHeightPx = 420,
  rowHeightPx = 56,
  initialScrollTopPx = 0,
  onScrollOffsetChange,
}) => {
  const [scrollTopPx, setScrollTopPx] = useState<number>(Math.max(0, initialScrollTopPx));

  const windowMetrics = computeVirtualWindowRange(
    paragraphs.length,
    viewportHeightPx,
    rowHeightPx,
    scrollTopPx,
    3
  );

  const visibleSlice = paragraphs.slice(windowMetrics.startIndex, windowMetrics.endIndex);

  const handleContainerScroll = (scrollEvent: React.UIEvent<HTMLDivElement>): void => {
    const nextScrollTop = Math.max(0, scrollEvent.currentTarget.scrollTop);
    setScrollTopPx(nextScrollTop);
    if (onScrollOffsetChange) {
      onScrollOffsetChange(nextScrollTop);
    }
  };

  return (
    <div
      onScroll={handleContainerScroll}
      style={{ height: `${viewportHeightPx}px`, overflowY: 'auto', position: 'relative', contain: 'layout style paint' }}
      className="rounded border border-slate-800 bg-slate-950/80 p-3"
      data-testid="virtual-block-window"
    >
      <div
        style={{ height: `${windowMetrics.totalHeightPx}px`, position: 'relative' }}
        data-testid="virtual-window-spacer"
      >
        <div
          style={{
            transform: `translateY(${windowMetrics.offsetY}px)`,
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
          }}
        >
          {visibleSlice.map((paragraphText, localIndex) => {
            const absoluteIndex = windowMetrics.startIndex + localIndex;
            const isHeading = paragraphText.trimStart().startsWith('#');
            const cleanedText = paragraphText.replace(/^#+\s*/, '');
            return (
              <div
                key={`virtual-row-${absoluteIndex}`}
                style={{ minHeight: `${Math.max(24, rowHeightPx)}px`, contain: 'layout style paint' }}
                className="sdui-virtual-row flex items-center border-b border-slate-900/60 px-2 py-1 text-sm text-slate-200"
                data-testid="virtual-mounted-node"
              >
                {isHeading ? (
                  <h3 className="font-bold text-blue-300">{renderInlineMarkdown(cleanedText)}</h3>
                ) : (
                  <p className="leading-relaxed">{renderInlineMarkdown(cleanedText)}</p>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
