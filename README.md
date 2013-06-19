Amazon Simple Product API 
==========================
A simple Python wrapper for the Amazon.com Product Advertising API. 
[![Build Status](https://secure.travis-ci.org/yoavaviram/python-amazon-simple-product-api.png?branch=master)](http://travis-ci.org/yoavaviram/python-amazon-simple-product-api)


Features
--------

* An object oriented interface to Amazon products
* Supports both item search and item lookup
* Compatible with Google App Engine


Dependencies
--------------
Before you get started, make sure you have:

* Installed [Bottlenose](https://github.com/lionheart/bottlenose) (`pip install bottlenose`)
* Installed lxml (`pip install lxml`)
* An Amazon Product Advertising account
* An AWS account


Usage
-----

Lookup:

     >>> from amazon.api import AmazonAPI
     >>> amazon = AmazonAPI(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOC_TAG)
     >>> product = amazon.lookup(ItemId='B0051QVF7A')
     >>> product.title
     'Kindle, Wi-Fi, 6" E Ink Display - for international shipment'
     >>> product.price_and_currency
     (89.0, 'USD')
     >>> product.ean
     '0814916014354'
     >>> product.large_image_url
     'http://ecx.images-amazon.com/images/I/411H%2B731ZzL.jpg'
     >>> product.get_attribute('Publisher')
     'Amazon Digital Services, Inc'
     >>> product.get_attributes(['ItemDimensions.Width', 'ItemDimensions.Height'])
     {'ItemDimensions.Width': '450', 'ItemDimensions.Height': '34'}

(the API wrapper also supports many other product attributes)

Lookup on amazon.de instead of amazon.com by setting the region:

     >>> from amazon.api import AmazonAPI
     >>> import bottlenose.api
     >>> region_options = bottlenose.api.SERVICE_DOMAINS.keys()
     >>> region_options
     ['US', 'FR', 'CN', 'UK', 'CA', 'DE', 'JP', 'IT', 'ES']
     >>> amazon_de = AmazonAPI(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOC_TAG, region="DE")
     >>> product = amazon_de.lookup(ItemId='B0051QVF7A')
     >>> product.title
     u'Kindle, WLAN, 15 cm (6 Zoll) E Ink Display, deutsches Men\xfc'
     >>> product.price_and_currency
     (99.0, 'EUR')

Batch lookup requests are also supported:

     >>> from amazon.api import AmazonAPI
     >>> amazon = AmazonAPI(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOC_TAG)
     >>> products = amazon.lookup(ItemId='B0051QVESA,B005DOK8NW,B005890G8Y,B0051VVOB2,B005890G8O')
     >>> len(products)
     5
     >>> products[0].asin
     'B0051QVESA'

Search:

     >>> from amazon.api import AmazonAPI
     >>> amazon = AmazonAPI(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOC_TAG)
     >>> products = amazon.search(Keywords='kindle', SearchIndex='All')
     >>> for i, product in enumerate(products):
     >>>     print "{0}. '{1}'".format(i, product.title)
     0. 'Kindle, Wi-Fi, 6" E Ink Display - includes Special Offers & Sponsored Screensavers'
     1. 'Kindle Fire, Full Color 7" Multi-touch Display, Wi-Fi'
     2. 'Kindle US Power Adapter (Not included with Kindle or Kindle Touch)'
     3. 'Kindle Touch, Wi-Fi, 6" E Ink Display - includes Special Offers & Sponsored Screensavers'
     4. 'Kindle Keyboard 3G, Free 3G + Wi-Fi, 6" E Ink Display - includes Special Offers & Sponsored Screensavers'
     5. 'Kindle Touch 3G, Free 3G + Wi-Fi, 6" E Ink Display - includes Special Offers & Sponsored Screensavers'
     ...
     49. 'Kindle Wireless Reading Device (6" Display, U.S. Wireless)'

The search method returns an iterable that will iterate through all products,
on all pages available. Additional pages are retrieved automatically as needed.
Keep in mind that Amazon limits the number of pages it makes available.

Valid values of SearchIndex are: 'All','Apparel','Appliances','ArtsAndCrafts','Automotive',
'Baby','Beauty','Blended','Books','Classical','Collectibles','DVD','DigitalMusic','Electronics',
'GiftCards','GourmetFood','Grocery','HealthPersonalCare','HomeGarden','Industrial','Jewelry',
'KindleStore','Kitchen','LawnAndGarden','Marketplace','MP3Downloads','Magazines','Miscellaneous',
'Music','MusicTracks','MusicalInstruments','MobileApps','OfficeProducts','OutdoorLiving','PCHardware',
'PetSupplies','Photo','Shoes','Software','SportingGoods','Tools','Toys','UnboxVideo','VHS','Video',
'VideoGames','Watches','Wireless','WirelessAccessories'

There is also a convenience method to search and return a list of the first N results:

     >>> from amazon.api import AmazonAPI
     >>> amazon = AmazonAPI(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOC_TAG)
     >>> products = amazon.search_n(1, Keywords='kindle', SearchIndex='All')
     >>> len(products)
     1
     >>> products[0].title
     'Kindle, Wi-Fi, 6" E Ink Display - includes Special Offers & Sponsored Screensavers'

Similarity Lookup:

     >>> from amazon.api import AmazonAPI
     >>> amazon = AmazonAPI(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOC_TAG)
     >>> products = amazon.similarity_lookup(ItemId='B0051QVESA,B005DOK8NW')
     >>> len(products)
     4

Browse Node Lookup:

     >>> from amazon.api import AmazonAPI
     >>> amazon = AmazonAPI(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOC_TAG)
     >>> bn = amazon.browse_node_lookup(BrowseNodeId=2642129011)
     >>> bn.name
     'eBook Readers'

For more information about these calls, please consult the [Product Advertising
API Developer Guide](http://docs.amazonwebservices.com/AWSECommerceService/latest/DG/index.html).

Tests
------
To run the test suite please follow these steps:

* Make sure [Nose](http://readthedocs.org/docs/nose/en/latest/) is installed: (`pip install nose`)
* Create a local file named: `test_settings.py` with the following variables set to the relevant values: `AMAZON_ACCESS_KEY`, `AMAZON_SECRET_KEY`, `AMAZON_ASSOC_TAG`
* Run `nosetests`

License
-------

Copyright &copy; 2012 Yoav Aviram

See LICENSE for details.

