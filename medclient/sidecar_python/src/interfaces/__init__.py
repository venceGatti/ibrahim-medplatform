"""Interface contracts and abstract protocols for MedClient."""
from .watchdog import IReverseWatchdog
from .database import ISqliteConnectionPool, IBlueGreenHotSwap
from .nlp import IMedicalSpellchecker, IInvertedLexicalDictionary, ISemanticEmbeddingEngine
from .diagnostic import (
    IRedFlagsInterceptor,
    ILogOddsRanker,
    IPertinentNegativesEvaluator,
    ILogSumExpNormalizer,
    IActiveDiscriminator,
)
from .pharmacology import (
    ICYP450Engine,
    IQTcCalculator,
    ITripleWhammyDetector,
    IRenalCalculator,
    IPharmacogenomicsEngine,
)
from .educational import (
    INLICrossEncoder,
    IStatefulDAGScenario,
    IFSRSScheduler,
    IReviewLoadBalancer,
)
from .sdui import ISDUISerializer

__all__ = [
    "IReverseWatchdog",
    "ISqliteConnectionPool",
    "IBlueGreenHotSwap",
    "IMedicalSpellchecker",
    "IInvertedLexicalDictionary",
    "ISemanticEmbeddingEngine",
    "IRedFlagsInterceptor",
    "ILogOddsRanker",
    "IPertinentNegativesEvaluator",
    "ILogSumExpNormalizer",
    "IActiveDiscriminator",
    "ICYP450Engine",
    "IQTcCalculator",
    "ITripleWhammyDetector",
    "IRenalCalculator",
    "IPharmacogenomicsEngine",
    "INLICrossEncoder",
    "IStatefulDAGScenario",
    "IFSRSScheduler",
    "IReviewLoadBalancer",
    "ISDUISerializer",
]
