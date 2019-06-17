from pm4py.algo.discovery.dfg.adapters.pandas import df_statistics
from pm4py.algo.discovery.inductive.versions.dfg import imdfb as inductive_miner
from pm4py.algo.filtering.pandas.auto_filter import auto_filter
from pm4py.visualization.common.utils import get_base64_from_gviz
from pm4py.visualization.process_tree import factory as pt_vis_factory
from pm4py.algo.filtering.pandas.attributes import attributes_filter
from pm4py.algo.filtering.pandas.start_activities import start_activities_filter
from pm4py.algo.filtering.pandas.end_activities import end_activities_filter
from pm4py.objects.log.util import xes
from pm4py.util import constants as pm4_constants
from pm4py.algo.filtering.common.filtering_constants import CASE_CONCEPT_NAME
import base64

from pm4pyws.util import constants


def apply(dataframe, parameters=None):
    """
    Gets the process tree using Inductive Miner Directly-Follows

    Parameters
    ------------
    dataframe
        Dataframe
    parameters
        Parameters of the algorithm

    Returns
    ------------
    base64
        Base64 of an SVG representing the model
    model
        Text representation of the model
    format
        Format of the model
    """
    if parameters is None:
        parameters = {}

    activity_key = parameters[pm4_constants.PARAMETER_CONSTANT_ACTIVITY_KEY] if pm4_constants.PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else xes.DEFAULT_NAME_KEY
    timestamp_key = parameters[pm4_constants.PARAMETER_CONSTANT_TIMESTAMP_KEY] if pm4_constants.PARAMETER_CONSTANT_TIMESTAMP_KEY in parameters else xes.DEFAULT_TIMESTAMP_KEY
    case_id_glue = parameters[pm4_constants.PARAMETER_CONSTANT_CASEID_KEY] if pm4_constants.PARAMETER_CONSTANT_CASEID_KEY in parameters else CASE_CONCEPT_NAME

    dataframe = attributes_filter.filter_df_keeping_spno_activities(dataframe, activity_key=activity_key,
                                                                    max_no_activities=constants.MAX_NO_ACTIVITIES)
    dataframe = auto_filter.apply_auto_filter(dataframe, parameters=parameters)

    activities_count = attributes_filter.get_attribute_values(dataframe, activity_key)
    activities = list(activities_count.keys())
    start_activities = list(start_activities_filter.get_start_activities(dataframe, parameters=parameters).keys())
    end_activities = list(end_activities_filter.get_end_activities(dataframe, parameters=parameters).keys())

    dfg = df_statistics.get_dfg_graph(dataframe, activity_key=activity_key, timestamp_key=timestamp_key, case_id_glue=case_id_glue)
    tree = inductive_miner.apply_tree_dfg(dfg, parameters, activities=activities, start_activities=start_activities, end_activities=end_activities)
    gviz = pt_vis_factory.apply(tree, parameters={"format": "svg"})

    gviz_base64 = base64.b64encode(str(gviz).encode('utf-8'))

    return get_base64_from_gviz(gviz), None, "", "parquet", activities, start_activities, end_activities, gviz_base64, []
