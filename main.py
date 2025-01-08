import sys
import os
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from GMAT.Integrated_Reasoning.main import GMAT_IR

from GMAT.Integrated_Reasoning.main import GMAT_IR
from GMAT.Quants.main import GMAT_Q
from GMAT.Verbal.main import GMAT_V
 
from GRE.Quants.main import GRE_Q
from GRE.Verbal.main import GRE_V


GMAT_Integrated_Reasoning = GMAT_IR()
GMAT_Quantitative = GMAT_Q()
GMAT_Verbal = GMAT_V()

GRE_Quantitative = GRE_Q()
GRE_Verbal = GRE_V()