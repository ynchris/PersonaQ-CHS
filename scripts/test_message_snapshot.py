import unittest
from unittest.mock import patch
import message_snapshot as module


class SnapshotTests(unittest.TestCase):
    def test_same_count_text_change_invalidates_snapshot(self):
        baseline=module.scope_snapshot('base')
        real_read=module.read
        def changed(path):
            value=real_read(path)
            if path.name=='catalog.working.json':
                row=next(r for r in value if r['status']=='draft_control_checked' and r['source'].startswith('export_base/'))
                row['translation']+='测试变更'
            return value
        with patch.object(module,'read',side_effect=changed):
            self.assertNotEqual(module.scope_snapshot('base'),baseline)
            self.assertEqual(module.scope_snapshot('0005'),self.dlc_snapshot)

    @classmethod
    def setUpClass(cls):
        cls.dlc_snapshot=module.scope_snapshot('0005')


if __name__=='__main__':unittest.main()
