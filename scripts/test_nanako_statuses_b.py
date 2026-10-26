import unittest
import test_nanako_statuses_a as common

class NanakoRemainingStatusesTests(common.NanakoStatusesTests):
    batch_name='404_nanako_statuses_b.generated.json'
    group_count=3

if __name__=='__main__':unittest.main()
