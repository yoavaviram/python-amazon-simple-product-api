import bottlenose
from lxml import objectify, etree
from django.conf import settings


API = bottlenose.Amazon(settings.AWS_KEY, settings.AWS_SECRET,
    AssociateTag=settings.AWS_ASSOCIATE_TAG)
"""Amazon API Instance"""


class AmazonException(Exception):
    """Base Class for Amazon Api Exceptions.
    """
    pass


class AsinNotFound(AmazonException):
    """ASIN Mot Found Exception.
    """
    pass


class LookupException(AmazonException):
    """Lookup Exception.
    """
    pass


class SearchException(AmazonException):
    """Search Exception.
    """
    pass


class NoMorePages(AmazonException):
    """No More Pages Exception.
    """
    pass


class AmazonProduct(object):
    """A Class encapsulating the Amazon Catalog.
    """

    def __init__(self, item, *args):
        """Initialize an Amazon Product Proxy.

        :param item:
            Lxml Item element.
        """
        self.item = item

    @classmethod
    def search(cls, **kwargs):
        """Search.

        :return:
            An :class:`~.AmazonSearch` iterable.
        """
        return AmazonSearch(**kwargs)

    @classmethod
    def get_by_asin(cls, asin):
        """Get an AmazonProduct by ASIN.

        Factory method.

        :param asin:
            Amazon ASIN - string.
        :return:
            :class:`~.AmazonProduct`
        """
        response = API.ItemLookup(ItemId=asin, ResponseGroup="Large")
        root = objectify.fromstring(response)
        if root.Items.Request.IsValid == 'False':
            code = root.Items.Request.Errors.Error.Code
            msg = root.Items.Request.Errors.Error.Message
            raise LookupException(
                "Amazon Product Lookup Error: '{0}', '{1}'".format(code, msg))
        if not hasattr(root.Items, 'Item'):
            raise AsinNotFound("ASIN not found: '{0}'".format(
                etree.tostring(root, pretty_print=True)))
        return cls(root.Items.Item)

    def _safe_get_element(self, path, root=None):
        """Safe Get Element.

        Get a child element of root (multiple levels deep) failing silently
        if any descendant does not exist.

        :param root:
            Lxml element.
        :param path"
            String path (i.e. 'Items.Item.Offers.Offer').
        :return:
            Element or None.
        """
        elements = path.split('.')
        parent = root or self.item
        for element in elements[:-1]:
            parent = getattr(parent, element, None)
            if parent is None:
                return None
        return getattr(parent, elements[-1], None)

    def _safe_get_element_text(self, path, root=None):
        """Safe get element text.

        Get element as string or None,
        :param root:
            Lxml element.
        :param path"
            String path (i.e. 'Items.Item.Offers.Offer').
        :return:
            String or None.
        """
        element = self._safe_get_element(path, root)
        if element:
            return element.text
        else:
            return None

    @property
    def price_and_currency(self):
        """Get Offer Price.

        Return price according to the following process:

        * If product has a sale return Sales Price, otherwise,
        * Return Price, otherwise,
        * Return lowest offer price, otherwise,
        * Return None.

        :return:
            A tuple containing:

                1. Float representation of price.
                2. ISO Currency code (string).
        """
        price = self._safe_get_element_text(
            'Offers.Offer.OfferListing.SalePrice.Amount')
        if price:
            currency = self._safe_get_element_text(
                'Offers.Offer.OfferListing.SalePrice.CurrencyCode')
        else:
            price = self._safe_get_element_text(
                'Offers.Offer.OfferListing.Price.Amount')
            if price:
                currency = self._safe_get_element_text(
                    'Offers.Offer.OfferListing.Price.CurrencyCode')
            else:
                price = self._safe_get_element_text(
                    'OfferSummary.LowestNewPrice.Amount')
                currency = self._safe_get_element_text(
                    'OfferSummary.LowestNewPrice.CurrencyCode')
        if price:
            return float(price) / 100, currency
        else:
            return None, None

    @property
    def asin(self):
        """ASIN (Amazon ID)

        :return:
            ASIN (string).
        """
        return self._safe_get_element_text('ASIN')

    @property
    def offer_url(self):
        """Offer URL

        :return:
            Offer URL (string).
        """
        return "{0}{1}/?tag={2}".format(
            settings.AMAZON_ASSOCIATES_BASE_URL,
            self.asin,
            settings.AMAZON_ASSOCIATES_TAG)

    @property
    def brand(self):
        """Brand.

        :return:
            Brand (string)
        """
        return self._safe_get_element_text('ItemAttributes.Brand')

    @property
    def isbn(self):
        """ISBN.

        :return:
            ISBN (string)
        """
        return self._safe_get_element_text('ItemAttributes.ISBN')

    @property
    def large_image_url(self):
        """Large Image URL.

        :return:
            Large image url (string)
        """
        return self._safe_get_element_text('LargeImage.URL')

    @property
    def medium_image_url(self):
        """Medium Image URL.

        :return:
            Medium image url (string)
        """
        return self._safe_get_element_text('MediumImage.URL')

    @property
    def small_image_url(self):
        """Small Image URL.

        :return:
            Small image url (string)
        """
        return self._safe_get_element_text('SmallImage.URL')

    @property
    def tiny_image_url(self):
        """Tiny Image URL.

        :return:
            Tiny image url (string)
        """
        return self._safe_get_element_text('TinyImage.URL')

    @property
    def reviews(self):
        """Customer Reviews.

        Get a iframe URL for customer reviews.
        :return:
            A tuple of: has_reviews (bool), reviews url (string)
        """
        iframe = self._safe_get_element_text('CustomerReviews.IFrameURL')
        has_reviews = self._safe_get_element_text('CustomerReviews.HasReviews')
        if has_reviews and has_reviews == 'true':
            has_reviews = True
        else:
            has_reviews = False
        return has_reviews, iframe

    @property
    def ean(self):
        """EAN.

        :return:
            EAN (string)
        """
        ean = self._safe_get_element_text('ItemAttributes.EAN')
        if ean is None:
            ean_list = self._safe_get_element_text('ItemAttributes.EANList')
            if ean_list:
                ean = self._safe_get_element_text('EANListElement',
                    root=ean_list[0])
        return ean

    @property
    def upc(self):
        """UPC.

        :return:
            UPC (string)
        """
        upc = self._safe_get_element_text('ItemAttributes.UPC')
        if upc is None:
            upc_list = self._safe_get_element_text('ItemAttributes.UPCList')
            if upc_list:
                upc = self._safe_get_element_text('UPCListElement',
                    root=upc_list[0])
        return upc

    @property
    def sku(self):
        """SKU.

        :return:
            SKU (string)
        """
        return self._safe_get_element_text('ItemAttributes.SKU')

    @property
    def mpn(self):
        """MPN.

        :return:
            MPN (string)
        """
        return self._safe_get_element_text('ItemAttributes.MPN')

    @property
    def model(self):
        """Model Name.

        :return:
            Model (string)
        """
        return self._safe_get_element_text('ItemAttributes.Model')

    @property
    def part_number(self):
        """Part Number.

        :return:
            Part Number (string)
        """
        return self._safe_get_element_text('ItemAttributes.PartNumber')

    @property
    def title(self):
        """Title.

        :return:
            Title (string)
        """
        return self._safe_get_element_text('ItemAttributes.Title')

    @property
    def editorial_review(self):
        """Editorial Review.

        Returns an editorial review text.
        :return:
            Editorial Review (string)
        """
        return self._safe_get_element_text(
            'EditorialReviews.EditorialReview.Content')

    @property
    def features(self):
        """Features.

        Returns a list of feature descriptions.
        :return:
            Returns a list of 'ItemAttributes.Feature' elements (strings).
        """
        features = []
        for feature in self._safe_get_element('ItemAttributes.Feature'):
            features.append(feature.text)
        return features

    @property
    def list_price(self):
        """List Price.
        """
        price = self._safe_get_element_text('ItemAttributes.ListPrice.Amount')
        currency = self._safe_get_element_text(
            'ItemAttributes.ListPrice.CurrencyCode')
        if price:
            return float(price) / 100, currency
        else:
            return None, None

    def get_attribute(self, name):
        """Get Attribute

        Get an attribute (child elements of 'ItemAttributes') value.

        :param name:
            Attribute name (string)
        :return:
            Attribute value (string) or None if not found.
        """
        return self._safe_get_element_text("ItemAttributes.{0}".format(name))

    def get_attributes(self, name_list):
        """Get Attributes

        Get a list of attributes as a name/value dictionary.

        :param name_list:
            A list of attribute names (strings).
        :return:
            A name/value dictionary (both names and values are strings).
        """
        properties = {}
        for name in name_list:
            value = self.get_attribute(name)
            if value is not None:
                properties[name] = value
        return properties


class AmazonSearch(object):
    """ Amazon Search.

    A class providing an iterable over amazon search results.
    """
    LIMIT = 10

    def __init__(self, **kwargs):
        """Initialise

        Initialise a search
        """
        self.kwargs = kwargs
        self.current_page = 1

    def __iter__(self):
        """Iterate.

        A generator which iterate over all paginated results
        returning :class:`~.AmazonProduct` for each item.

        :return:
            Yields a :class:`~.AmazonProduct` for each result item.
        """
        for page in self.iterate_pages():
            for item in page.Items.Item:
                yield AmazonProduct(item)

    def iterate_pages(self):
        """Iterate Pages.

        A generator which iterates over all pages.
        Keep in mind that Amazon limits the number of pages it makes available.

        :return:
            Yields lxml root elements.
        """
        try:
            while True:
                yield self._query(ItemPage=self.current_page, **self.kwargs)
                self.current_page += 1
        except NoMorePages:
            pass

    def _query(self, **kwargs):
        """Query.

        Query Amazon search and check for errors.

        :return:
            An lxml root element.
        """
        response = API.ItemSearch(ResponseGroup="Large", **kwargs)
        root = objectify.fromstring(response)
        if root.Items.Request.IsValid == 'False':
            code = root.Items.Request.Errors.Error.Code
            msg = root.Items.Request.Errors.Error.Message
            if code == 'AWS.ParameterOutOfRange':
                raise NoMorePages(msg)
            else:
                raise SearchException(
                    "Amazon Search Error: '{0}', '{1}'".format(code, msg))
        return root
