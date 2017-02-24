#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from nose.tools import assert_equals, assert_true, assert_false, assert_raises
from flaky import flaky

import time
import datetime
from decimal import Decimal
from amazon.api import (AmazonAPI,
                        CartException,
                        CartInfoMismatchException,
                        SearchException,
                        AmazonSearch,
                        AsinNotFound)

_AMAZON_ACCESS_KEY = None
_AMAZON_SECRET_KEY = None
_AMAZON_ASSOC_TAG = None


import os
if 'AMAZON_ACCESS_KEY' in os.environ and 'AMAZON_SECRET_KEY' in os.environ and 'AMAZON_ASSOC_TAG' in os.environ:
    _AMAZON_ACCESS_KEY = os.environ['AMAZON_ACCESS_KEY']
    _AMAZON_SECRET_KEY = os.environ['AMAZON_SECRET_KEY']
    _AMAZON_ASSOC_TAG = os.environ['AMAZON_ASSOC_TAG']
else:
    from test_settings import (AMAZON_ACCESS_KEY,
                               AMAZON_SECRET_KEY,
                               AMAZON_ASSOC_TAG)
    _AMAZON_ACCESS_KEY = AMAZON_ACCESS_KEY
    _AMAZON_SECRET_KEY = AMAZON_SECRET_KEY
    _AMAZON_ASSOC_TAG = AMAZON_ASSOC_TAG


TEST_ASIN = "0312098286"

PRODUCT_ATTRIBUTES = [
    'asin', 'author', 'binding', 'brand', 'browse_nodes', 'ean', 'edition',
    'editorial_review', 'eisbn', 'features', 'get_parent', 'isbn', 'label',
    'large_image_url', 'list_price', 'manufacturer', 'medium_image_url',
    'model', 'mpn', 'offer_url', 'parent_asin', 'part_number',
    'price_and_currency', 'publication_date', 'publisher', 'region',
    'release_date', 'reviews', 'sku', 'small_image_url', 'tiny_image_url',
    'title', 'upc'
]

CART_ATTRIBUTES = [
    'cart_id', 'purchase_url', 'amount', 'formatted_price', 'currency_code',
    'url_encoded_hmac', 'hmac'
]

CART_ITEM_ATTRIBUTES = [
    'cart_item_id', 'asin', 'title', 'amount', 'formatted_price',
    'currency_code', 'quantity', 'product_group',
]

CACHE = {}


def cache_writer(url, response):
    CACHE[url] = response


def cache_reader(url):
    return CACHE.get(url, None)


def cache_clear():
    global CACHE
    CACHE = {}

def delay_rerun(err, *args):
    time.sleep(5)
    return True


class TestAmazonApi(unittest.TestCase):
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
            _AMAZON_ACCESS_KEY,
            _AMAZON_SECRET_KEY,
            _AMAZON_ASSOC_TAG,
            CacheReader=cache_reader,
            CacheWriter=cache_writer,
            MaxQPS=0.5
        )

    @flaky(max_runs=3, rerun_filter=delay_rerun)
    def test_lookup(self):
        """Test Product Lookup.

        Tests that a product lookup for a kindle returns results and that the
        main methods are working.
        """
        product = self.amazon.lookup(ItemId="B00ZV9PXP2")
        assert_true('Kindle' in product.title)
        assert_equals(product.ean, '0848719083774')
        assert_equals(
            product.large_image_url,
            'https://images-na.ssl-images-amazon.com/images/I/51hrdzXLUHL.jpg'
        )
        assert_equals(
            product.get_attribute('Publisher'),
            'Amazon'
        )
        assert_equals(product.get_attributes(
            ['ItemDimensions.Width', 'ItemDimensions.Height']),
            {'ItemDimensions.Width': '450', 'ItemDimensions.Height': '36'})
        assert_true(len(product.browse_nodes) > 0)
        assert_true(product.price_and_currency[0] is not None)
        assert_true(product.price_and_currency[1] is not None)
        assert_equals(product.browse_nodes[0].id, 2642129011)
        assert_equals(product.browse_nodes[0].name, 'eBook Readers')

    @flaky(max_runs=3, rerun_filter=delay_rerun)
    def test_lookup_nonexistent_asin(self):
        """Test Product Lookup with a nonexistent ASIN.

        Tests that a product lookup for a nonexistent ASIN raises AsinNotFound.
        """
        assert_raises(AsinNotFound, self.amazon.lookup, ItemId="ABCD1234")

    @flaky(max_runs=3, rerun_filter=delay_rerun)
    def test_bulk_lookup(self):
        """Test Baulk Product Lookup.

        Tests that a bulk product lookup request returns multiple results.
        """
        asins = [TEST_ASIN, 'B00BWYQ9YE',
                 'B00BWYRF7E', 'B00D2KJDXA']
        products = self.amazon.lookup(ItemId=','.join(asins))
        assert_equals(len(products), len(asins))
        for i, product in enumerate(products):
            assert_equals(asins[i], product.asin)

    @flaky(max_runs=3, rerun_filter=delay_rerun)
    def test_lookup_bulk(self):
        """Test Bulk Product Lookup.

        Tests that a bulk product lookup request returns multiple results.
        """
        asins = [TEST_ASIN, 'B00BWYQ9YE',
                 'B00BWYRF7E', 'B00D2KJDXA']
        products = self.amazon.lookup_bulk(ItemId=','.join(asins))
        assert_equals(len(products), len(asins))
        for i, product in enumerate(products):
            assert_equals(asins[i], product.asin)

    @flaky(max_runs=3, rerun_filter=delay_rerun)
    def test_lookup_bulk_empty(self):
        """Test Bulk Product Lookup With No Results.

        Tests that a bulk product lookup request with no results
        returns an empty list.
        """
        asins = ['not-an-asin', 'als-not-an-asin']
        products = self.amazon.lookup_bulk(ItemId=','.join(asins))
        assert_equals(type(products), list)
        assert_equals(len(products), 0)

    @flaky(max_runs=3, rerun_filter=delay_rerun)
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

    @flaky(max_runs=3, rerun_filter=delay_rerun)
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

    @flaky(max_runs=3, rerun_filter=delay_rerun)
    def test_search_iterate_pages(self):
        products = self.amazon.search(Keywords='internet of things oreilly',
                                      SearchIndex='Books')
        assert_false(products.is_last_page)
        for product in products:
            pass
        assert_true(products.is_last_page)


    @flaky(max_runs=3, rerun_filter=delay_rerun)
    def test_search_no_results(self):
        """Test Product Search with no results.

        Tests that a product search with that returns no results throws a
        SearchException.
        """
        products = self.amazon.search(Title='no-such-thing-on-amazon',
                                      SearchIndex='Automotive')
        assert_raises(SearchException, next, (x for x in products))

    def test_amazon_api_defaults_to_US(self):
        """Test Amazon API defaults to the US store."""
        amazon = AmazonAPI(
            _AMAZON_ACCESS_KEY,
            _AMAZON_SECRET_KEY,
            _AMAZON_ASSOC_TAG
        )
        assert_equals(amazon.api.Region, "US")

    @flaky(max_runs=3, rerun_filter=delay_rerun)
    def test_search_amazon_uk(self):
        """Test Poduct Search on Amazon UK.

        Tests that a product search on Amazon UK is working and that the
        currency of any of the returned products is GBP. The test fails if no
        results were returned.
        """
        amazon = AmazonAPI(
            _AMAZON_ACCESS_KEY,
            _AMAZON_SECRET_KEY,
            _AMAZON_ASSOC_TAG,
            region="UK"
        )
        assert_equals(amazon.api.Region, "UK", "Region has not been set to UK")

        products = amazon.search(Keywords='Kindle', SearchIndex='All')
        currencies = [product.price_and_currency[1] for product in products]
        assert_true(len(currencies), "No products found")

        is_gbp = 'GBP' in currencies
        assert_true(is_gbp, "Currency is not GBP, cannot be Amazon UK, though")

    @flaky(max_runs=3, rerun_filter=delay_rerun)
    def test_similarity_lookup(self):
        """Test Similarity Lookup.

        Tests that a similarity lookup for a kindle returns 10 results.
        """
        products = self.amazon.similarity_lookup(ItemId=TEST_ASIN)
        assert_true(len(products) > 5)

    @flaky(max_runs=3, rerun_filter=delay_rerun)
    def test_product_attributes(self):
        """Test Product Attributes.

        Tests that all product that are supposed to be accessible are.
        """
        product = self.amazon.lookup(ItemId=TEST_ASIN)
        for attribute in PRODUCT_ATTRIBUTES:
            getattr(product, attribute)

    @flaky(max_runs=3, rerun_filter=delay_rerun)
    def test_browse_node_lookup(self):
        """Test Browse Node Lookup.

        Test that a lookup by Brose Node ID returns appropriate node.
        """
        bnid = 2642129011
        bn = self.amazon.browse_node_lookup(BrowseNodeId=bnid)[0]
        assert_equals(bn.id, bnid)
        assert_equals(bn.name, 'eBook Readers')
        assert_equals(bn.is_category_root, False)

    @flaky(max_runs=3, rerun_filter=delay_rerun)
    def test_obscure_date(self):
        """Test Obscure Date Formats

        Test a product with an obscure date format
        """
        product = self.amazon.lookup(ItemId="0933635869")
        assert_equals(product.publication_date.year, 1992)
        assert_equals(product.publication_date.month, 5)
        assert_true(isinstance(product.publication_date, datetime.date))

    @flaky(max_runs=3, rerun_filter=delay_rerun)
    def test_single_creator(self):
        """Test a product with a single creator
        """
        product = self.amazon.lookup(ItemId="B00005NZJA")
        creators = dict(product.creators)
        assert_equals(creators[u"Jonathan Davis"], u"Narrator")
        assert_equals(len(creators.values()), 2)

    @flaky(max_runs=3, rerun_filter=delay_rerun)
    def test_multiple_creators(self):
        """Test a product with multiple creators
        """
        product = self.amazon.lookup(ItemId="B007V8RQC4")
        creators = dict(product.creators)
        assert_equals(creators[u"John Gregory Betancourt"], u"Editor")
        assert_equals(creators[u"Colin Azariah-Kribbs"], u"Editor")
        assert_equals(len(creators.values()), 2)

    @flaky(max_runs=3, rerun_filter=delay_rerun)
    def test_no_creators(self):
        """Test a product with no creators
        """
        product = self.amazon.lookup(ItemId="8420658537")
        assert_false(product.creators)

    @flaky(max_runs=3, rerun_filter=delay_rerun)
    def test_single_editorial_review(self):
        product = self.amazon.lookup(ItemId="1930846258")
        expected = u'In the title piece, Alan Turing'
        assert_equals(product.editorial_reviews[0][:len(expected)], expected)
        assert_equals(product.editorial_review, product.editorial_reviews[0])
        assert_equals(len(product.editorial_reviews), 1)

    @flaky(max_runs=3, rerun_filter=delay_rerun)
    def test_multiple_editorial_reviews(self):
        product = self.amazon.lookup(ItemId="B01HQA6EOC")
        expected = u'<p>Introducing an instant classic—master storyteller'
        assert_equals(product.editorial_reviews[0][:len(expected)], expected)
        expected = u'<strong>An Amazon Best Book of February 2017:</strong>'
        assert_equals(product.editorial_reviews[1][:len(expected)], expected)
        # duplicate data, amazon user data is great...
        expected = u'<p>Introducing an instant classic—master storyteller'
        assert_equals(product.editorial_reviews[2][:len(expected)], expected)

        assert_equals(len(product.editorial_reviews), 3)

    @flaky(max_runs=3, rerun_filter=delay_rerun)
    def test_languages_english(self):
        """Test Language Data

        Test an English product
        """
        product = self.amazon.lookup(ItemId="1930846258")
        assert_true('english' in product.languages)
        assert_equals(len(product.languages), 1)

    @flaky(max_runs=3, rerun_filter=delay_rerun)
    def test_languages_spanish(self):
        """Test Language Data

        Test an English product
        """
        product = self.amazon.lookup(ItemId="8420658537")
        assert_true('spanish' in product.languages)
        assert_equals(len(product.languages), 1)

    def test_region(self):
        amazon = AmazonAPI(_AMAZON_ACCESS_KEY, _AMAZON_SECRET_KEY,
                           _AMAZON_ASSOC_TAG)
        assert_equals(amazon.region, 'US')

        # old 'region' parameter
        amazon = AmazonAPI(_AMAZON_ACCESS_KEY, _AMAZON_SECRET_KEY,
                           _AMAZON_ASSOC_TAG, region='UK')
        assert_equals(amazon.region, 'UK')

        # kwargs method
        amazon = AmazonAPI(_AMAZON_ACCESS_KEY, _AMAZON_SECRET_KEY,
                           _AMAZON_ASSOC_TAG, Region='UK')
        assert_equals(amazon.region, 'UK')

    @flaky(max_runs=3, rerun_filter=delay_rerun)
    def test_is_adult(self):
        product = self.amazon.lookup(ItemId="B01E7P9LEE")
        assert_true(product.is_adult is not None)

    @flaky(max_runs=3, rerun_filter=delay_rerun)
    def test_product_group(self):
        product = self.amazon.lookup(ItemId="B01LXM0S25")
        assert_equals(product.product_group, 'DVD')

        product = self.amazon.lookup(ItemId="B01NBTSVDN")
        assert_equals(product.product_group, 'Digital Music Album')

    @flaky(max_runs=3, rerun_filter=delay_rerun)
    def test_product_type_name(self):
        product = self.amazon.lookup(ItemId="B01NBTSVDN")
        assert_equals(product.product_type_name, 'DOWNLOADABLE_MUSIC_ALBUM')

    @flaky(max_runs=3, rerun_filter=delay_rerun)
    def test_formatted_price(self):
        product = self.amazon.lookup(ItemId="B01NBTSVDN")
        assert_equals(product.formatted_price, '$12.49')

    @flaky(max_runs=3, rerun_filter=delay_rerun)
    def test_price_and_currency(self):
        product = self.amazon.lookup(ItemId="B01NBTSVDN")
        price, currency = product.price_and_currency
        assert_equals(price, Decimal('12.49'))
        assert_equals(currency, 'USD')

    @flaky(max_runs=3, rerun_filter=delay_rerun)
    def test_list_price(self):
        product = self.amazon.lookup(ItemId="B01NBTSVDN")
        price, currency = product.list_price
        assert_equals(price, Decimal('12.49'))
        assert_equals(currency, 'USD')

    @flaky(max_runs=3, rerun_filter=delay_rerun)
    def test_running_time(self):
        product = self.amazon.lookup(ItemId="B01NBTSVDN")
        assert_equals(product.running_time, '774')

    @flaky(max_runs=3, rerun_filter=delay_rerun)
    def test_studio(self):
        product = self.amazon.lookup(ItemId="B01NBTSVDN")
        assert_equals(product.studio, 'Atlantic Records UK')

    @flaky(max_runs=3, rerun_filter=delay_rerun)
    def test_is_preorder(self):
        product = self.amazon.lookup(ItemId="B01NBTSVDN")
        assert_equals(product.is_preorder, '1')

    @flaky(max_runs=3, rerun_filter=delay_rerun)
    def test_detail_page_url(self):
        product = self.amazon.lookup(ItemId="B01NBTSVDN")
        assert_true(product.detail_page_url.startswith('https://www.amazon.com/%C3%B7-Deluxe-Ed-Sheeran/dp/B01NBTSVDN'))

    @flaky(max_runs=3, rerun_filter=delay_rerun)
    def test_availability(self):
        product = self.amazon.lookup(ItemId="B00ZV9PXP2")
        assert_equals(product.availability, 'Usually ships in 24 hours')

        product = self.amazon.lookup(ItemId="1491914254") # pre-order book
        assert_equals(product.availability, 'Not yet published')

        product = self.amazon.lookup(ItemId="B000SML2BQ") # late availability
        assert_true(product.availability is not None)

        product = self.amazon.lookup(ItemId="B01LTHP2ZK") # unavailable 
        assert_true(product.availability is None)

    @flaky(max_runs=3, rerun_filter=delay_rerun)
    def test_availability_type(self):
        product = self.amazon.lookup(ItemId="B00ZV9PXP2")
        assert_equals(product.availability_type, 'now')

        product = self.amazon.lookup(ItemId="1491914254") # pre-order book
        assert_equals(product.availability_type, 'now')

        product = self.amazon.lookup(ItemId="B00ZV9PXP2") # late availability
        assert_equals(product.availability_type, 'now')

        product = self.amazon.lookup(ItemId="B01LTHP2ZK") # unavailable
        assert_true(product.availability_type is None)

    @flaky(max_runs=3, rerun_filter=delay_rerun)
    def test_availability_min_max_hours(self):
        product = self.amazon.lookup(ItemId="B00ZV9PXP2")
        assert_equals(product.availability_min_hours, '0')
        assert_equals(product.availability_max_hours, '0')


    def test_kwargs(self):
        amazon = AmazonAPI(_AMAZON_ACCESS_KEY, _AMAZON_SECRET_KEY,
                           _AMAZON_ASSOC_TAG, MaxQPS=0.7)

    @flaky(max_runs=3, rerun_filter=delay_rerun)
    def test_images(self):
        """Test images property

        Test that the images property has a value when using the
        Images ResponseGroup
        """
        product = self.amazon.lookup(ResponseGroup='Images',
                                     ItemId='B00TSVVNQC')
        assert_equals(type(product.images), list)
        assert_equals(len(product.images), 7)


class TestAmazonCart(unittest.TestCase):
    def setUp(self):
        self.amazon = AmazonAPI(
            _AMAZON_ACCESS_KEY,
            _AMAZON_SECRET_KEY,
            _AMAZON_ASSOC_TAG,
            CacheReader=cache_reader,
            CacheWriter=cache_writer,
            MaxQPS=0.5
        )

    def test_cart_clear_required_params(self):
        assert_raises(CartException, self.amazon.cart_clear, None, None)
        assert_raises(CartException, self.amazon.cart_clear, 'NotNone',
                      None)
        assert_raises(CartException, self.amazon.cart_clear, None,
                      'NotNone')

    def build_cart_object(self):
        product = self.amazon.lookup(ItemId="B00ZV9PXP2")
        return self.amazon.cart_create(
            {
                'offer_id': product.offer_id,
                'quantity': 1
            }
        )

    def test_cart_create_single_item(self):
        cart = self.build_cart_object()
        assert_equals(len(cart), 1)

    def test_cart_create_multiple_item(self):
        product1 = self.amazon.lookup(ItemId="B00ZV9PXP2")
        product2 = self.amazon.lookup(ItemId=TEST_ASIN)
        asins = [product1.asin, product2.asin]

        cart = self.amazon.cart_create([
            {
                'offer_id': product1._safe_get_element(
                    'Offers.Offer.OfferListing.OfferListingId'),
                'quantity': 1
            },
            {
                'offer_id': product2._safe_get_element(
                    'Offers.Offer.OfferListing.OfferListingId'),
                'quantity': 1
            },
        ])
        assert_equals(len(cart), 2)
        for item in cart:
            assert_true(item.asin in asins)

    def test_cart_clear(self):
        cart = self.build_cart_object()
        new_cart = self.amazon.cart_clear(cart.cart_id, cart.hmac)
        assert_true(new_cart._safe_get_element('Cart.Request.IsValid'))

    def test_cart_clear_wrong_hmac(self):
        cart = self.build_cart_object()
        # never use urlencoded hmac, as library encodes as well. Just in case
        # hmac = url_encoded_hmac we add some noise
        hmac = cart.url_encoded_hmac + '%3d'
        assert_raises(CartInfoMismatchException, self.amazon.cart_clear,
                      cart.cart_id, hmac)

    def test_cart_attributes(self):
        cart = self.build_cart_object()
        for attribute in CART_ATTRIBUTES:
            getattr(cart, attribute)

    def test_cart_item_attributes(self):
        cart = self.build_cart_object()
        for item in cart:
            for attribute in CART_ITEM_ATTRIBUTES:
                getattr(item, attribute)

    def test_cart_get(self):
        # We need to flush the cache here so we will get a new cart that has
        # not been used in test_cart_clear
        cache_clear()
        cart = self.build_cart_object()
        fetched_cart = self.amazon.cart_get(cart.cart_id, cart.hmac)

        assert_equals(fetched_cart.cart_id, cart.cart_id)
        assert_equals(len(fetched_cart), len(cart))

    def test_cart_get_wrong_hmac(self):
        # We need to flush the cache here so we will get a new cart that has
        # not been used in test_cart_clear
        cache_clear()
        cart = self.build_cart_object()
        assert_raises(CartInfoMismatchException, self.amazon.cart_get,
                      cart.cart_id, cart.hmac + '%3d')

    def test_cart_add(self):
        cart = self.build_cart_object()
        product = self.amazon.lookup(ItemId=TEST_ASIN)
        item = {
            'offer_id': product._safe_get_element(
                'Offers.Offer.OfferListing.OfferListingId'),
            'quantity': 1
        }
        new_cart = self.amazon.cart_add(item, cart.cart_id, cart.hmac)
        assert_true(len(new_cart) > len(cart))

    def test_cart_modify(self):
        cart = self.build_cart_object()
        cart_item_id = None
        for item in cart:
            cart_item_id = item.cart_item_id
        item = {'cart_item_id': cart_item_id, 'quantity': 3}
        new_cart = self.amazon.cart_modify(item, cart.cart_id, cart.hmac)
        assert_equals(new_cart[cart_item_id].quantity, '3')

    def test_cart_delete(self):
        cart = self.build_cart_object()
        cart_item_id = None
        for item in cart:
            cart_item_id = item.cart_item_id
        item = {'cart_item_id': cart_item_id, 'quantity': 0}
        new_cart = self.amazon.cart_modify(item, cart.cart_id, cart.hmac)
        assert_raises(KeyError, new_cart.__getitem__, cart_item_id)

if __name__ == '__main__':
    unittest.main()
