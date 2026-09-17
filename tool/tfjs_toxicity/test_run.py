"""Check that corrupted or incomplete inference cannot produce a false pass."""

import copy
import json
import unittest

from run import HERE, validate


class ValidationTest(unittest.TestCase):
    def setUp(self):
        self.reference = json.loads((HERE / "toxicity-reference.json").read_text())
        records = []
        for indexes in ([0, 1, 2], [3]):
            records.append({
                "inputs": [self.reference["inputs"][i] for i in indexes],
                "tfjs": "1.2.2", "threshold": 0.85,
                "backend": "webgl", "webglVersion": 2,
                "hasWebGLContext": True, "drawCount": 10,
                "glError": 0, "floatRendering": True, "bufferSupported": True,
                "renderer": "llvmpipe",
                "predictions": [{"label": head["label"],
                                 "results": [copy.deepcopy(head["results"][i]) for i in indexes]}
                                for head in self.reference["predictions"]]})
        self.payload = {"rows": 5, "classifications": records,
                        "initialTable": [[str(head["results"][i]["match"]).lower()
                                          for head in self.reference["predictions"]]
                                         for i in range(3)]}

    def check(self, payload, mode="software", evidence=None):
        return validate(payload, self.reference, "webgl2", mode, evidence or [])

    def test_reference_matches(self):
        self.assertEqual(self.check(self.payload), ([], 0))

    def test_incomplete_or_corrupted_results_fail(self):
        for mutation in ("missing_head", "duplicate_head", "nan", "shape", "fallback",
                         "input", "threshold", "missing_buffer", "probability"):
            with self.subTest(mutation=mutation):
                payload = copy.deepcopy(self.payload)
                record = payload["classifications"][0]
                heads = record["predictions"]
                if mutation == "missing_head":
                    heads.pop()
                elif mutation == "duplicate_head":
                    heads[1] = heads[0]
                elif mutation == "nan":
                    heads[0]["results"][0]["probabilities"][0] = float("nan")
                elif mutation == "shape":
                    heads[0]["results"].pop()
                elif mutation == "fallback":
                    record["backend"] = "cpu"
                elif mutation == "input":
                    record["inputs"][0] = "another input"
                elif mutation == "threshold":
                    record["threshold"] = 0.5
                elif mutation == "missing_buffer":
                    record["bufferSupported"] = False
                elif mutation == "probability":
                    heads[0]["results"][0]["probabilities"] = [0.5, 0.5]
                self.assertTrue(self.check(payload)[0])

    def test_gpu_requires_renderer_and_matching_process_evidence(self):
        self.assertTrue(self.check(self.payload, "gpu", ["process"])[0])
        for record in self.payload["classifications"]:
            record["renderer"] = "NVIDIA GeForce RTX 3050"
        self.assertTrue(self.check(self.payload, "gpu")[0])
        self.assertEqual(self.check(self.payload, "gpu", ["process"]), ([], 0))


if __name__ == "__main__":
    unittest.main()
