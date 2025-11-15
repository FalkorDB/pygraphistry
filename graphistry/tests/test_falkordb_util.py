# -*- coding: utf-8 -*-

import datetime as dt
import os
import pandas as pd
import pytest

try:
    import falkordb
    has_falkordb = True
except (ImportError, ModuleNotFoundError):
    has_falkordb = False

if has_falkordb:
    from graphistry.falkordb_util import (
        falkordb_df_to_pd_df,
        node_id_key,
        node_type_key,
        start_node_id_key,
        end_node_id_key,
        relationship_id_key,
        relationship_type_key,
    )


@pytest.mark.skipif(not has_falkordb, reason="No falkordb")
def test_falkordb_df_to_pd_df_basics():
    rec = {"x": 1, "b": True, "s": "abc", "a": [1, 2, 3], "d": {"r": "v"}, "mt": None}
    df = pd.DataFrame([rec])
    df2 = falkordb_df_to_pd_df(df)
    assert df2.dtypes.to_dict() == {
        "x": "int",
        "b": "bool",
        "s": "object",
        "a": "object",
        "d": "object",
        "mt": "object",
    }
    d = df2.to_dict(orient="records")[0]
    assert d == rec


@pytest.mark.skipif(not has_falkordb, reason="No falkordb")
def test_falkordb_df_to_pd_df_basics_na():
    recs = {
        "x": [1, None],
        "b": [True, None],
        "s": ["abc", None],
        "a": [[1, 2, 3], None],
        "d": [{"r": "v"}, None],
        "mt": [None, None],
    }
    df = pd.DataFrame(recs)
    df2 = falkordb_df_to_pd_df(df)
    assert df2.dtypes.to_dict() == {
        "x": "float64",
        "b": "object",
        "s": "object",
        "a": "object",
        "d": "object",
        "mt": "object",
    }
    d = df2.to_dict(orient="records")[0]
    assert d == {k: recs[k][0] for k in recs.keys()}


@pytest.mark.skipif(not has_falkordb, reason="No falkordb")
@pytest.mark.skipif(
    not ("WITH_FALKORDB" in os.environ) or os.environ["WITH_FALKORDB"] != "1",
    reason="No WITH_FALKORDB=1",
)
class TestFalkorDBConnector:
    @classmethod
    def setup_class(cls):
        import graphistry
        from falkordb import FalkorDB

        FALKORDB_CREDS = {
            "host": "falkordb-test",
            "port": 6379,
            "password": "test"
        }
        graphistry.pygraphistry.PyGraphistry._is_authenticated = True
        db = FalkorDB(**FALKORDB_CREDS)
        graphistry.register(api=3, falkordb=db)
        cls.db = db
        cls.graph_name = 'social'

    def test_falkordb_conn_setup(self):
        assert True is True

    def test_falkordb_ready(self):
        import graphistry
        
        g = graphistry.falkordb_cypher(
            self.graph_name,
            "MATCH (a)-[b]-(c) WHERE a <> c RETURN a, b, c LIMIT 1"
        )
        assert len(g._nodes) >= 2

    def test_falkordb_no_edges(self):
        import graphistry
        
        with pytest.warns(RuntimeWarning):
            g = graphistry.falkordb_cypher(
                self.graph_name,
                "MATCH (a) RETURN a LIMIT 1"
            )

        assert len(g._nodes) >= 1
        assert len(g._edges) == 0
        for col in [node_id_key, node_type_key]:
            assert col in g._nodes
        for col in [
            start_node_id_key,
            end_node_id_key,
            relationship_id_key,
            relationship_type_key,
        ]:
            assert col in g._edges

    def test_falkordb_no_nodes(self):
        import graphistry
        
        with pytest.warns(RuntimeWarning):
            g = graphistry.falkordb_cypher(
                self.graph_name,
                "MATCH (a) WHERE a.name = 'NONEXISTENT' RETURN a LIMIT 1"
            )

        assert len(g._nodes) == 0
        assert len(g._edges) == 0
        for col in [node_id_key, node_type_key]:
            assert col in g._nodes
        for col in [
            start_node_id_key,
            end_node_id_key,
            relationship_id_key,
            relationship_type_key,
        ]:
            assert col in g._edges

    def test_falkordb_some_edges(self):
        import graphistry
        
        g = graphistry.falkordb_cypher(
            self.graph_name,
            "MATCH (a)-[b]-(c) WHERE a <> c RETURN a, b, c LIMIT 1"
        )
        assert len(g._nodes) >= 2
        assert len(g._edges) >= 1

        for col in [node_id_key, node_type_key]:
            assert col in g._nodes

        for col in [
            start_node_id_key,
            end_node_id_key,
            relationship_id_key,
            relationship_type_key,
        ]:
            assert col in g._edges
