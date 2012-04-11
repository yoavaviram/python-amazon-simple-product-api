from unittest import TestCase

from nose.tools import assert_equals, assert_true

from amazon.api import AmazonAPI
from test_settings import (AMAZON_ACCESS_KEY,
                           AMAZON_SECRET_KEY,
                           AMAZON_ASSOC_TAG)


class TestAmazonApi(TestCase):
    """Test Amazon API

    Test Class for Amazon simple API wrapper.
    """
    def setUp(self):
        """Set Up.

        Initialize the Amazon API wrapper. The following values:

        * AMAZON_ACCESS_KEY
        * AMAZON_SECRET_KEY
        * AMAZON_ASSOC_TAG

        Are imported from a custom file named: 'test_settings.py'
        """
        self.amazon = AmazonAPI(AMAZON_ACCESS_KEY,
            AMAZON_SECRET_KEY, AMAZON_ASSOC_TAG)

    def test_lookup(self):
        """Test Product Lookup.

        Tests that a product lookup for a kindle returns results and that the
        main methods are working.
        """
        product = self.amazon.get_by_asin("B0051QVF7A")
        assert_equals(product.title,
            'Kindle, Wi-Fi, 6" E Ink Display - for international shipment')
        assert_equals(product.price_and_currency, (109.0, 'USD'))
        assert_equals(product.ean, '0814916014354')
        assert_equals(product.large_image_url,
            'http://ecx.images-amazon.com/images/I/411H%2B731ZzL.jpg')
        assert_equals(product.get_attribute('Publisher'),
            'Amazon Digital Services, Inc')
        assert_equals(product.get_attributes(
            ['ItemDimensions.Width', 'ItemDimensions.Height']),
            {'ItemDimensions.Width': '450', 'ItemDimensions.Height': '34'})

    def test_search(self):
        """Test Product Search.

        Tests that a product search is working (by testing that results are
        returned). And that each result has a title attribute. The test
        fails if no results where returned.
        """
        products = self.amazon.search(Keywords='kindle', SearchIndex='All')
        for product in products:
            assert_true(hasattr(product, 'title'))
            break
        else:
            assert_true(False, 'No search results returned.')
