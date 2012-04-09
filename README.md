amazon-simple-product-api
==========================

Description
-----------

A simple Python wrapper for the Amazon.com Product Advertising API.


Features
--------

* An object based interface to Amazon products.
* Supports both item search and item lookup.


Prerequisite
--------------
Before you get started, make sure you have:

* Installed [Bottlenose](https://github.com/dlo/bottlenose): >>> pip install bottlenose
* An Amazon Product Advertising account
* An AWS account


Usage
-----

Lookup::

     >>> from amazon.api import AmazonAPI
     >>> amazon = AmazonAPI(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOC_TAG)
     >>> product = amazon.get_by_asin("B0051QVF7A")
     >>> product.title
     'Kindle, Wi-Fi, 6" E Ink Display - for international shipment'
     >>> product.price_and_currency
     (109.0, 'USD')
     >>> product.ean
     '0814916014354'
     >>> product.large_image_url
     'http://ecx.images-amazon.com/images/I/411H%2B731ZzL.jpg'
     >>> product.get_attribute('Publisher')
     'Amazon Digital Services, Inc'
     >>> product.get_attributes(['ItemDimensions.Width', 'ItemDimensions.Height'])
     {'ItemDimensions.Width': '450', 'ItemDimensions.Height': '34'}

Please note that the API wrapper supports many other product properties as well.

Search::
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

For more information about these calls, please consult the [Product Advertising
API Developer Guide](http://docs.amazonwebservices.com/AWSECommerceService/latest/DG/index.html).


License
-------

Copyright &copy; 2012 Yoav Aviram

See LICENSE for details.

