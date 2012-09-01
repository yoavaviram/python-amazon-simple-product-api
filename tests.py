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
        product = self.amazon.lookup(ItemId="B0051QVF7A")
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

    def test_batch_lookup(self):
        """Test Batch Product Lookup.

        Tests that a batch product lookup request returns multiple results.
        """
        asins = ['B0051QVESA', 'B005DOK8NW', 'B005890G8Y',
                 'B0051VVOB2', 'B005890G8O']
        products = self.amazon.lookup(ItemId=','.join(asins))
        assert_equals(len(products), 5)
        for i, product in enumerate(products):
            assert_equals(asins[i], product.asin)

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

    def test_search_n(self):
        """Test Product Search N.

        Tests that a product search n is working by testing that N results are
        returned.
        """
        products = self.amazon.search_n(1, Keywords='kindle',
            SearchIndex='All')
        assert_equals(len(products), 1)

    def test_amazon_api_defaults_to_US(self):
        """Test Amazon API defaults to the US store."""
        amazon = AmazonAPI(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY,
            AMAZON_ASSOC_TAG)
        assert_equals(amazon.api.Region, "US")

    def test_search_amazon_germany(self):
        """Test Poduct Search on Amazon UK.
        
        Tests that a product search on Amazon UK is working and that the
        currency of any of the returned products is GBP. The test fails if no
        results were returned.
        """
        amazon = AmazonAPI(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY,
            AMAZON_ASSOC_TAG, region="UK")
        assert_equals(amazon.api.Region, "UK", "Region has not been set to UK")

        products = amazon.search(Keywords='Kindle', SearchIndex='All')
        currencies = [product.price_and_currency[1] for product in products]
        assert_true(len(currencies), "No products found")

        is_gbp = 'GBP' in currencies
        assert_true(is_gbp, "Currency is not GBP, cannot be Amazon UK, though")
