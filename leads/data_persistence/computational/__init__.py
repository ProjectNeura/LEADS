try:
    from leads.data_persistence.computational.gpu import *
except ImportError:
    from leads.data_persistence.computational.stable import *
