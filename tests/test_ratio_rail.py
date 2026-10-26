"""Scripted host/model tests. No actual VM or network consensus is simulated as evidence."""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import types
import unittest

class Return:
    def __init__(self, value):
        self.calldata = value

class Map(dict):
    @classmethod
    def __class_getitem__(cls, value):
        return cls

identity = lambda f: f
host = types.SimpleNamespace(
    Contract=object,
    public=types.SimpleNamespace(view=identity, write=identity),
    message=types.SimpleNamespace(sender_address="0x" + "1" * 40),
    nondet=types.SimpleNamespace(),
    vm=types.SimpleNamespace(Return=Return))
sdk = types.ModuleType("genlayer")
sdk.gl, sdk.TreeMap, sdk.u32 = host, Map, int
sys.modules["genlayer"] = sdk
spec = importlib.util.spec_from_file_location("rail", Path(__file__).parents[1]/"contracts/ratio_rail.py")
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)

def exact(a, b):
    return {"status": "EXACT", "from_count": a, "to_count": b}

class ProtocolTests(unittest.TestCase):
    def setUp(self):
        host.message.sender_address = "0x" + "1" * 40
        self.c = r.RatioRail()
        self.c.books, self.c.owner_counts = Map(), Map()
        self.rid = self.c.create("test-kit", "AA-1 identical metal clips", json.dumps(["case", "box", "piece"]))
        self.calls = 0
        self.responses = []
        def prompt(*args, **kwargs):
            self.calls += 1
            value = self.responses.pop(0)
            if isinstance(value, Exception):
                raise value
            return value
        def nondet(leader, validator):
            value = leader()
            if not validator(Return(value)):
                raise Exception("MOCK_CONSENSUS_REJECTED")
            return value
        host.nondet.exec_prompt = prompt
        host.vm.run_nondet_unsafe = nondet

    def book(self):
        return json.loads(self.c.get_book(self.rid))

    def link(self, a, b, value, independent=None, text=None):
        self.responses = [value, independent if independent is not None else copy.deepcopy(value)]
        return json.loads(self.c.link(self.rid, self.book()["revision"], a, b,
                         text or f"Fixed declared packaging equality number {len(self.book()['attempts'])}."))

    def ready(self):
        self.link(0, 1, exact(1, 6))
        self.link(1, 2, exact(1, 4))

    def test_transitive_conflict_cannot_change_active_conversion(self):
        self.ready()
        b = self.link(0, 2, exact(1, 20))
        a = b["attempts"][-1]
        self.assertEqual(a["outcome"], "CONFLICT")
        self.assertEqual(a["witness"]["existing_path"]["ratio"], [24, 1])
        self.assertEqual(a["witness"]["cycle_product"], [5, 6])
        self.assertEqual(len(b["edges"]), 2)
        self.assertEqual(b["state"], "READY")
        self.c.freeze(self.rid, 3)
        result = json.loads(self.c.convert(self.rid, 2, 0, 25))
        self.assertEqual((result["numerator"], result["denominator"]), (25, 24))
        self.assertEqual((result["whole_units"], result["remainder_numerator"]), (1, 1))

    def test_scaled_semantic_equalities_are_equivalent(self):
        self.assertTrue(r.equivalent(Return(exact(2, 12)), lambda: exact(1, 6)))
        self.assertFalse(r.equivalent(Return(exact(2, 12)), lambda: exact(6, 1)))
        self.link(0, 1, exact(2, 12), exact(1, 6))
        self.assertEqual(self.book()["edges"][0]["ratio"], [6, 1])

    def test_validator_disagreement_rolls_back_before_storage(self):
        before = self.c.get_book(self.rid)
        with self.assertRaisesRegex(Exception, "CONSENSUS"):
            self.link(0, 1, exact(1, 6), exact(1, 8))
        self.assertEqual(self.c.get_book(self.rid), before)

    def test_unresolved_stays_out_of_graph(self):
        b = self.link(0, 1, {"status":"UNRESOLVED","from_count":0,"to_count":0})
        self.assertEqual(b["attempts"][0]["outcome"], "UNRESOLVED")
        self.assertEqual(b["edges"], [])
        self.assertEqual(b["state"], "OPEN")

    def test_nonreturn_and_bad_validator_fail_closed(self):
        self.assertFalse(r.equivalent(object(), lambda: exact(1, 2)))
        self.assertFalse(r.equivalent(Return(exact(1, 2)), lambda: {"status":"EXACT"}))
        def fails():
            raise RuntimeError("provider")
        self.assertFalse(r.equivalent(Return(exact(1, 2)), fails))

    def test_strict_model_schema_and_counts(self):
        bad = [exact(True, 2), exact(1.0, 2), exact(0, 2), exact(1, 1000001),
               {"status":"EXACT","from_count":1,"to_count":2,"reason":"extra"},
               {"status":"UNRESOLVED","from_count":1,"to_count":0},
               '{"status":"EXACT","from_count":1,"from_count":2,"to_count":6}']
        for item in bad:
            with self.subTest(item=item), self.assertRaises(Exception):
                r.normalize(item)

    def test_malformed_or_provider_errors_do_not_write(self):
        before = self.c.get_book(self.rid)
        for value in [{"bad":1}, RuntimeError("provider")]:
            with self.assertRaises(Exception):
                self.link(0, 1, value)
            self.assertEqual(self.c.get_book(self.rid), before)

    def test_duplicate_input_and_stale_revision_skip_model(self):
        text = "Exactly one case contains six boxes of this product."
        self.link(0, 1, exact(1, 6), text=text)
        calls = self.calls
        with self.assertRaisesRegex(Exception, "DUPLICATE_INPUT"):
            self.c.link(self.rid, 1, 0, 1, text)
        with self.assertRaisesRegex(Exception, "STALE_REVISION"):
            self.c.link(self.rid, 0, 0, 2, text)
        self.assertEqual(calls, self.calls)

    def test_other_owner_cannot_mutate_but_can_read(self):
        self.ready()
        host.message.sender_address = "0x" + "2" * 40
        self.assertTrue(self.c.get_book(self.rid))
        with self.assertRaisesRegex(Exception, "OWNER_ONLY"):
            self.c.freeze(self.rid, 2)
        with self.assertRaisesRegex(Exception, "OWNER_ONLY"):
            self.c.link(self.rid, 2, 0, 2, "Exactly one case contains 24 pieces.")

    def test_disconnected_book_cannot_freeze_or_convert(self):
        self.link(0, 1, exact(1, 6))
        with self.assertRaisesRegex(Exception, "NOT_READY"):
            self.c.freeze(self.rid, 1)
        with self.assertRaisesRegex(Exception, "NOT_FROZEN"):
            self.c.convert(self.rid, 0, 1, 1)

    def test_redundant_inverse_is_not_new_edge(self):
        self.ready()
        b = self.link(2, 0, exact(24, 1))
        self.assertEqual(b["attempts"][-1]["outcome"], "REDUNDANT")
        self.assertEqual(len(b["edges"]), 2)
        self.assertTrue(all(s["reverse"] for s in b["attempts"][-1]["witness"]["steps"]))

    def test_freeze_is_terminal_and_hash_bound(self):
        self.ready()
        b = json.loads(self.c.freeze(self.rid, 2))
        self.assertEqual(b["table"][0][2], [24, 1])
        self.assertEqual(b["table_hash"], r.hash_value({"scope_hash":b["scope_hash"],"table":b["table"]}))
        with self.assertRaisesRegex(Exception, "FROZEN"):
            self.c.link(self.rid, 3, 0, 2, "Exactly one case contains 24 pieces.")
        with self.assertRaisesRegex(Exception, "NOT_READY"):
            self.c.freeze(self.rid, 3)

    def test_amounts_zero_identity_bounds_and_no_float(self):
        self.ready()
        self.c.freeze(self.rid, 2)
        self.assertEqual(json.loads(self.c.convert(self.rid, 0, 2, 0))["denominator"], 1)
        self.assertEqual(json.loads(self.c.convert(self.rid, 2, 2, 37))["numerator"], 37)
        for value in [-1, 1.5, True, 1000000000001]:
            with self.assertRaisesRegex(Exception, "AMOUNT_BOUND"):
                self.c.convert(self.rid, 0, 2, value)

    def test_fractional_group_relation_and_path_composition(self):
        self.link(0, 1, exact(2, 3))
        self.link(1, 2, exact(3, 5))
        self.c.freeze(self.rid, 2)
        self.assertEqual(json.loads(self.c.convert(self.rid, 0, 2, 1))["numerator"], 5)
        self.assertEqual(json.loads(self.c.convert(self.rid, 0, 2, 1))["denominator"], 2)

    def test_bounds_and_unit_uniqueness(self):
        for units in [["box"], ["Box","box"], [" case","box"]]:
            with self.assertRaises(Exception):
                self.c.create("other", "AA-1 identical metal clips", json.dumps(units))
        for a, b in [(0,0),(-1,1),(0,3),(True,1)]:
            with self.assertRaisesRegex(Exception, "ENDPOINTS"):
                self.c.link(self.rid, 0, a, b, "A fixed packaging count of six.")
        self.assertEqual(self.calls, 0)

    def test_owner_book_limit_and_namespace_isolation(self):
        for i in range(11):
            self.c.create(f"kit-{i}", "AA-1 identical metal clips", '["box","piece"]')
        with self.assertRaisesRegex(Exception, "BOOK_LIMIT"):
            self.c.create("excess", "AA-1 identical metal clips", '["box","piece"]')
        host.message.sender_address = "0x" + "2" * 40
        other = self.c.create("test-kit", "AA-1 identical metal clips", '["box","piece"]')
        self.assertNotEqual(other, self.rid)

    def test_attempt_budget_includes_rejections(self):
        for i in range(12):
            self.link(0, 1, {"status":"UNRESOLVED","from_count":0,"to_count":0})
        with self.assertRaisesRegex(Exception, "ATTEMPT_LIMIT"):
            self.c.link(self.rid, 12, 0, 1, "Exactly one case has six boxes.")
        self.assertEqual(self.book()["edges"], [])

    def test_order_independent_consistent_graph_results(self):
        edges = [{"from":0,"to":1,"ratio":[3,2],"attempt":0},
                 {"from":1,"to":2,"ratio":[10,3],"attempt":1},
                 {"from":0,"to":2,"ratio":[5,1],"attempt":2}]
        for a in range(3):
            for b in range(3):
                self.assertEqual(r.path(edges,a,b)["ratio"],r.path(list(reversed(edges)),a,b)["ratio"])

if __name__ == "__main__":
    unittest.main()
