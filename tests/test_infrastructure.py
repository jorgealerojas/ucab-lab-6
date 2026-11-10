from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
TEMPLATE = (ROOT / "infra" / "lab-stack.yaml").read_text(encoding="utf-8")


class InfrastructureContractTests(unittest.TestCase):
    def test_week_one_architecture_is_present(self) -> None:
        required_types = {
            "AWS::ElasticLoadBalancingV2::LoadBalancer",
            "AWS::ElasticLoadBalancingV2::TargetGroup",
            "AWS::EC2::LaunchTemplate",
            "AWS::AutoScaling::AutoScalingGroup",
            "AWS::AutoScaling::ScalingPolicy",
            "AWS::CloudWatch::Dashboard",
            "AWS::CloudWatch::Alarm",
            "AWS::S3::Bucket",
        }
        for resource_type in required_types:
            self.assertIn(f"Type: {resource_type}", TEMPLATE)

    def test_scaling_bounds_and_metric_are_fixed(self) -> None:
        self.assertRegex(TEMPLATE, r'MinSize: "1"')
        self.assertRegex(TEMPLATE, r'DesiredCapacity: "1"')
        self.assertRegex(TEMPLATE, r'MaxSize: "3"')
        self.assertIn("MetricName: RequestCountPerTarget", TEMPLATE)
        self.assertGreaterEqual(TEMPLATE.count("PolicyType: StepScaling"), 2)
        self.assertRegex(TEMPLATE, r"Threshold: 300\b")

    def test_application_ingress_comes_from_load_balancer_group(self) -> None:
        application_group = TEMPLATE.split("  ApplicationSecurityGroup:", 1)[1].split(
            "\n  AccessLogBucket:", 1
        )[0]
        self.assertIn("SourceSecurityGroupId: !Ref LoadBalancerSecurityGroup", application_group)
        self.assertNotIn("CidrIp: 0.0.0.0/0", application_group)

    def test_template_has_no_ssh_ingress(self) -> None:
        self.assertNotRegex(TEMPLATE, re.compile(r"FromPort:\s*22\b"))


if __name__ == "__main__":
    unittest.main()
