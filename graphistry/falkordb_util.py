# -*- coding: utf-8 -*-

import pandas as pd
from datetime import datetime
from .pygraphistry import util
from .util import setup_logger
logger = setup_logger(__name__)

node_id_key = u'_falkordb_node_id_key'
node_type_key = u'type'
node_label_prefix_key = u'_lbl_'
start_node_id_key = u'_falkordb_start_node_id_key'
end_node_id_key = u'_falkordb_end_node_id_key'
relationship_id_key = u'_falkordb_relationship_id'
relationship_type_key = u'type'

t0 = datetime.min.time()


def to_falkordb_db(db=None):
    """
    Convert a FalkorDB connection dict or object to a FalkorDB instance.
    
    :param db: FalkorDB instance or dict with connection params
    :return: FalkorDB instance or None
    """
    if db is None:
        return None
    try:
        from falkordb import FalkorDB
        if isinstance(db, FalkorDB):
            return db
        # If dict is provided, create FalkorDB instance
        return FalkorDB(**db)
    except ImportError:
        raise FalkorDBSupportModuleNotFound()


def falkordb_result_to_edges_dataframe(result):
    """
    Convert FalkorDB query result to edges DataFrame.
    
    :param result: FalkorDB QueryResult object
    :return: pandas DataFrame with edge data
    """
    edges_list = []
    
    if not hasattr(result, 'result_set') or not result.result_set:
        util.warn('Query returned no edges; may have surprising visual results or need to add missing columns for encodings')
        return pd.DataFrame({
            relationship_id_key: pd.Series([], dtype='int32'),
            relationship_type_key: pd.Series([], dtype='object'),
            start_node_id_key: pd.Series([], dtype='int32'),
            end_node_id_key: pd.Series([], dtype='int32')
        })
    
    # Extract edges from result set
    for record in result.result_set:
        for item in record:
            if hasattr(item, 'src_node') and hasattr(item, 'dest_node'):
                # This is an edge
                edge_dict = {
                    relationship_id_key: item.id,
                    relationship_type_key: item.relation,
                    start_node_id_key: item.src_node.id,
                    end_node_id_key: item.dest_node.id,
                }
                # Add edge properties
                if hasattr(item, 'properties') and item.properties:
                    edge_dict.update(item.properties)
                edges_list.append(edge_dict)
    
    if len(edges_list) == 0:
        util.warn('Query returned no edges; may have surprising visual results or need to add missing columns for encodings')
        return pd.DataFrame({
            relationship_id_key: pd.Series([], dtype='int32'),
            relationship_type_key: pd.Series([], dtype='object'),
            start_node_id_key: pd.Series([], dtype='int32'),
            end_node_id_key: pd.Series([], dtype='int32')
        })
    
    df = pd.DataFrame(edges_list)
    return falkordb_df_to_pd_df(df)


def falkordb_result_to_nodes_dataframe(result) -> pd.DataFrame:
    """
    Convert FalkorDB query result to nodes DataFrame.
    
    :param result: FalkorDB QueryResult object
    :return: pandas DataFrame with node data
    """
    nodes_dict = {}  # Use dict to deduplicate by node ID
    
    if not hasattr(result, 'result_set') or not result.result_set:
        util.warn('Query returned no nodes')
        return pd.DataFrame({
            node_id_key: pd.Series([], dtype='int32'),
            node_type_key: pd.Series([], dtype='object')
        })
    
    # Extract nodes from result set
    for record in result.result_set:
        for item in record:
            if hasattr(item, 'labels') and hasattr(item, 'properties'):
                # This is a node
                node_id = item.id
                if node_id not in nodes_dict:
                    node_dict = {
                        node_id_key: node_id,
                        node_type_key: ",".join(sorted([str(label) for label in (item.labels or [])]))
                    }
                    # Add node properties
                    if item.properties:
                        node_dict.update(item.properties)
                    # Add label boolean columns
                    if item.labels:
                        for label in item.labels:
                            node_dict[node_label_prefix_key + str(label)] = True
                    nodes_dict[node_id] = node_dict
            elif hasattr(item, 'src_node') and hasattr(item, 'dest_node'):
                # This is an edge, extract src and dest nodes
                for node in [item.src_node, item.dest_node]:
                    node_id = node.id
                    if node_id not in nodes_dict:
                        node_dict = {
                            node_id_key: node_id,
                            node_type_key: ",".join(sorted([str(label) for label in (node.labels or [])]))
                        }
                        # Add node properties
                        if hasattr(node, 'properties') and node.properties:
                            node_dict.update(node.properties)
                        # Add label boolean columns
                        if node.labels:
                            for label in node.labels:
                                node_dict[node_label_prefix_key + str(label)] = True
                        nodes_dict[node_id] = node_dict
    
    if len(nodes_dict) == 0:
        util.warn('Query returned no nodes')
        return pd.DataFrame({
            node_id_key: pd.Series([], dtype='int32'),
            node_type_key: pd.Series([], dtype='object')
        })
    
    df = pd.DataFrame(list(nodes_dict.values()))
    return falkordb_df_to_pd_df(df)


def falkordb_val_to_pd_val(v):
    """
    Convert FalkorDB value types to pandas-compatible values.
    
    :param v: Value from FalkorDB
    :return: Pandas-compatible value
    """
    if v is None:
        return v
    
    try:
        v_type = type(v).__name__
    except:
        return v
    
    # Handle datetime types (FalkorDB uses Python datetime types from dateutil)
    if isinstance(v, datetime):
        return v
    
    # Handle timedelta/duration
    from dateutil.relativedelta import relativedelta
    if isinstance(v, relativedelta):
        # Convert relativedelta to ISO format string for storage
        # FalkorDB duration format
        return f"P{v.years}Y{v.months}M{v.days}D"
    
    return v


def falkordb_df_to_pd_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert FalkorDB DataFrame to pandas DataFrame with proper type handling.
    
    :param df: Input DataFrame with FalkorDB types
    :return: DataFrame with pandas-compatible types
    """
    out_df: pd.DataFrame = df.copy(deep=False)  # type: ignore
    for col in df.columns:
        if df[col].dtype.name == 'object':
            out_df[col] = df[col].apply(falkordb_val_to_pd_val)
    return out_df


class FalkorDBSupportModuleNotFound(Exception):
    def __init__(self):
        super(FalkorDBSupportModuleNotFound, self).__init__(
            "The falkordb module was not found but is required for pygraphistry FalkorDB support. "
            "Try running `!pip install --user graphistry[falkordb]` or `!pip install --user falkordb`."
        )
