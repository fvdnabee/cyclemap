"""Unit tests for the import_masto script."""
import unittest

from cyclemap.scripts.import_masto import add_geo_json

TEST_CASES = [
    ("<p>Shiny new wheels for the bicycle 👍Curious how smooth the bearings in the SP pv-8 (front) and Shimano FH-T670 (rear) hubs will roll!</p>",
        None),
    ("<a href=\"https://osm.org/?mlat=35.866667&amp;mlon=128.6\" rel=\"nofollow noopener noreferrer\" target=\"_blank\"><span class=\"invisible\">\
https://</span><span class=\"ellipsis\">osm.org/?mlat=35.866667&amp;mlon=1</span><span class=\"invisible\">28.6</span></a>",
        (128.6, 35.866667)),
    ("<a href=\"https://osm.org/?mlat=34.033333333333&amp;mlon=-5\" rel=\"nofollow noopener noreferrer\" target=\"_blank\"><span class=\"invisible\">\
https://</span><span class=\"ellipsis\">osm.org/?mlat=34.033333333333&amp;</span><span class=\"invisible\">mlon=-5</span></a>",
        (-5, 34.033333333333)),
    ("<a href=\"https://osm.org/?mlat=34&amp;mlon=-5\" rel=\"nofollow noopener noreferrer\" target=\"_blank\"><span class=\"invisible\">https://\
</span><span class=\"ellipsis\">osm.org/?mlat=34.033333333333&amp;</span><span class=\"invisible\">mlon=-5</span></a>",
        (-5, 34)),
    ("<a href=\"https://osm.org/?mlat=-34.2&amp;mlon=-5\" rel=\"nofollow noopener noreferrer\" target=\"_blank\"><span class=\"invisible\">https://\
</span><span class=\"ellipsis\">osm.org/?mlat=34.033333333333&amp;</span><span class=\"invisible\">mlon=-5</span></a>",
        (-5, -34.2)),
    ("<a href=\"https://www.osm.org/?mlat=50.81053&amp;mlon=5.67085\" rel=\"nofollow noopener noreferrer\" target=\"_blank\"><span class=\"invisible\">\
https://www.</span><span class=\"ellipsis\">osm.org/?mlat=50.81053&amp;mlon=5.</span><span class=\"invisible\">67085</span></a>",
        (5.67085, 50.81053))
]

class TestImportMasto(unittest.TestCase):
    """Unit tests for the import_masto script."""
    def test_geo_location_parsing(self):
        """Unit test add_geo_json method."""
        for content, expected_geo_loc in TEST_CASES:
            status = {'content': content}
            add_geo_json(status)

            if expected_geo_loc is None:
                self.assertTrue('location' not in content)
            else:
                self.assertSequenceEqual(status['location']['coordinates'], expected_geo_loc)


if __name__ == '__main__':
    unittest.main()
