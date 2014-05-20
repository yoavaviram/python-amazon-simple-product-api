from unittest import TestCase

from nose.tools import assert_equals, assert_true

import datetime
from amazon.api import AmazonAPI
from test_settings import (AMAZON_ACCESS_KEY,
                           AMAZON_SECRET_KEY,
                           AMAZON_ASSOC_TAG)


PRODUCT_ATTRIBUTES = [
    'asin', 'author', 'binding', 'brand', 'browse_nodes', 'ean', 'edition',
    'editorial_review', 'eisbn', 'features', 'get_parent', 'isbn', 'label',
    'large_image_url', 'list_price', 'manufacturer', 'medium_image_url',
    'model', 'mpn', 'offer_url', 'parent_asin', 'part_number',
    'price_and_currency', 'publication_date', 'publisher', 'region',
    'release_date', 'reviews', 'sku', 'small_image_url', 'tiny_image_url',
    'title', 'upc'
]


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
        self.amazon = AmazonAPI(
            AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOC_TAG)

    def test_lookup(self):
        """Test Product Lookup.

        Tests that a product lookup for a kindle returns results and that the
        main methods are working.
        """
        product = self.amazon.lookup(ItemId="B007HCCNJU")
        assert_true('Kindle' in product.title)
        assert_equals(product.ean, '0814916017775')
        assert_equals(
            product.large_image_url,
            'http://ecx.images-amazon.com/images/I/41VZlVs8agL.jpg'
        )
        assert_equals(
            product.get_attribute('Publisher'),
            'Amazon'
        )
        assert_equals(product.get_attributes(
            ['ItemDimensions.Width', 'ItemDimensions.Height']),
            {'ItemDimensions.Width': '650', 'ItemDimensions.Height': '130'})
        assert_true(len(product.browse_nodes) > 0)
        assert_true(product.price_and_currency[0] is not None)
        assert_true(product.price_and_currency[1] is not None)
        assert_equals(product.browse_nodes[0].id, 2642129011)
        assert_equals(product.browse_nodes[0].name, 'eBook Readers')

    def test_batch_lookup(self):
        """Test Batch Product Lookup.

        Tests that a batch product lookup request returns multiple results.
        """
        asins = ['B00AWH595M', 'B007HCCNJU', 'B00BWYQ9YE',
                 'B00BWYRF7E', 'B00D2KJDXA']
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
        products = self.amazon.search_n(
            1,
            Keywords='kindle',
            SearchIndex='All'
        )
        assert_equals(len(products), 1)

    def test_amazon_api_defaults_to_US(self):
        """Test Amazon API defaults to the US store."""
        amazon = AmazonAPI(
            AMAZON_ACCESS_KEY,
            AMAZON_SECRET_KEY,
            AMAZON_ASSOC_TAG
        )
        assert_equals(amazon.api.Region, "US")

    def test_search_amazon_uk(self):
        """Test Poduct Search on Amazon UK.

        Tests that a product search on Amazon UK is working and that the
        currency of any of the returned products is GBP. The test fails if no
        results were returned.
        """
        amazon = AmazonAPI(
            AMAZON_ACCESS_KEY,
            AMAZON_SECRET_KEY,
            AMAZON_ASSOC_TAG,
            region="UK"
        )
        assert_equals(amazon.api.Region, "UK", "Region has not been set to UK")

        products = amazon.search(Keywords='Kindle', SearchIndex='All')
        currencies = [product.price_and_currency[1] for product in products]
        assert_true(len(currencies), "No products found")

        is_gbp = 'GBP' in currencies
        assert_true(is_gbp, "Currency is not GBP, cannot be Amazon UK, though")

    def test_similarity_lookup(self):
        """Test Similarity Lookup.

        Tests that a similarity lookup for a kindle returns 10 results.
        """
        products = self.amazon.similarity_lookup(ItemId="B0051QVF7A")
        assert_equals(len(products), 10)

    def test_product_attributes(self):
        """Test Product Attributes.

        Tests that all product that are supposed to be accessible are.
        """
        product = self.amazon.lookup(ItemId="B0051QVF7A")
        for attribute in PRODUCT_ATTRIBUTES:
            getattr(product, attribute)

    def test_browse_node_lookup(self):
        """Test Browse Node Lookup.

        Test that a lookup by Brose Node ID returns appropriate node.
        """
        bnid = 2642129011
        bn = self.amazon.browse_node_lookup(BrowseNodeId=bnid)[0]
        assert_equals(bn.id, bnid)
        assert_equals(bn.name, 'eBook Readers')
        assert_equals(bn.is_category_root, False)

    def test_obscure_date(self):
        """Test Obscure Date Formats

        Test a product with an obscure date format
        """
        product = self.amazon.lookup(ItemId="0933635869")
        assert_equals(product.publication_date.year, 1992)
        assert_equals(product.publication_date.month, 5)
        assert_true(isinstance(product.publication_date, datetime.date))

    def test_languages_english(self):
        """Test Language Data

        Test an English product
        """
        product = self.amazon.lookup(ItemId="1930846258")
        assert_true('english' in product.languages)
        assert_equals(len(product.languages), 1)

    def test_languages_spanish(self):
        """Test Language Data

        Test an English product
        """
        product = self.amazon.lookup(ItemId="8420658537")
        assert_true('spanish' in product.languages)
        assert_equals(len(product.languages), 1)


