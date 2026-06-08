# Domain Classification

Maps extraction source domains to backend domain types. Used during
Phase 3 to decide whether extracted data can be ingested into a
domain-specific table.

## Media

| Domain | Provider | Defaults |
|---|---|---|
| netflix.com | NETFLIX | content_type=series, media_category=video |
| spotify.com | SPOTIFY | content_type=song, media_category=audio |
| youtube.com | YOUTUBE | content_type=short_video, media_category=video |
| music.youtube.com | YOUTUBE | content_type=song, media_category=audio |
| disneyplus.com | DISNEY_PLUS | content_type=series, media_category=video |
| hulu.com | HULU | content_type=series, media_category=video |
| max.com | HBO_MAX | content_type=series, media_category=video |
| hbomax.com | HBO_MAX | content_type=series, media_category=video |
| primevideo.com | PRIME_VIDEO | content_type=series, media_category=video |
| paramountplus.com | PARAMOUNT_PLUS | content_type=series, media_category=video |
| crave.ca | CRAVE | content_type=series, media_category=video |
| tv.apple.com | APPLE_TV | content_type=series, media_category=video |
| music.apple.com | APPLE_MUSIC | content_type=song, media_category=audio |
| podcasts.apple.com | APPLE_PODCASTS | content_type=podcast, media_category=audio |
| tiktok.com | TIKTOK | content_type=short_video, media_category=video |
| tsn.ca | TSN | content_type=live_sports, media_category=live_event |

## Commerce

| Domain | Provider | Defaults |
|---|---|---|
| ubereats.com | UBER_EATS | activity_type=FOOD_DELIVERY |
| doordash.com | DOORDASH | activity_type=FOOD_DELIVERY |
| grubhub.com | GRUBHUB | activity_type=FOOD_DELIVERY |
| skipthedishes.com | SKIPTHEDISHES | activity_type=FOOD_DELIVERY |
| instacart.com | INSTACART_USA | activity_type=GROCERY |
| instacart.ca | INSTACART_CANADA | activity_type=GROCERY |
| amazon.com | AMAZON_USA | activity_type=ONLINE_PURCHASE |
| amazon.ca | AMAZON_CANADA | activity_type=ONLINE_PURCHASE |
| walmart.com | WALMART | activity_type=ONLINE_PURCHASE |
| bestbuy.com | BEST_BUY | activity_type=ELECTRONICS |
| costco.com | COSTCO_USA | activity_type=ONLINE_PURCHASE |
| costco.ca | COSTCO_CANADA | activity_type=ONLINE_PURCHASE |
| canadiantire.ca | CANADIAN_TIRE | activity_type=HOME_IMPROVEMENT |
| homedepot.com | HOME_DEPOT | activity_type=HOME_IMPROVEMENT |
| ikea.com | IKEA | activity_type=FURNITURE |
| wayfair.com | WAYFAIR | activity_type=FURNITURE |
| etsy.com | ETSY | activity_type=ONLINE_PURCHASE |
| ebay.com | EBAY | activity_type=ONLINE_PURCHASE |
| apple.com | APPLE_STORE | activity_type=ELECTRONICS |
| starbucks.com | STARBUCKS | activity_type=COFFEE |
| mcdonalds.com | MCDONALDS | activity_type=RESTAURANT |
| timhortons.com | TIM_HORTONS_CANADA | activity_type=COFFEE |
| ticketmaster.com | TICKETMASTER | activity_type=ONLINE_PURCHASE |
| opentable.com | OPENTABLE | activity_type=RESTAURANT |

## Travel

| Domain | Provider | Defaults |
|---|---|---|
| uber.com | UBER | activity_type=RIDESHARE |
| lyft.com | LYFT | activity_type=RIDESHARE |
| airbnb.com | AIRBNB | activity_type=HOTEL |
| expedia.com | EXPEDIA | activity_type=FLIGHT |
| hotels.com | HOTELS_COM | activity_type=HOTEL |
| booking.com | BOOKING_COM | activity_type=HOTEL |
| vrbo.com | VRBO | activity_type=HOTEL |
| kayak.com | KAYAK | activity_type=FLIGHT |
| priceline.com | PRICELINE | activity_type=FLIGHT |
| tripadvisor.com | TRIPADVISOR | activity_type=HOTEL |
| turo.com | TURO | activity_type=CAR_RENTAL |
| avis.com | AVIS | activity_type=CAR_RENTAL |
| lime.com | LIME | activity_type=RIDESHARE |
| aircanada.com | AIR_CANADA | activity_type=FLIGHT |
| hilton.com | HILTON_HONORS | activity_type=HOTEL |
| ihg.com | IHG_REWARDS | activity_type=HOTEL |
| viator.com | VIATOR | activity_type=ACTIVITY |
| getyourguide.com | GET_YOUR_GUIDE | activity_type=ACTIVITY |

## Field Naming Hints

When authoring recipes for classified domains, prefer these field names
so the ingest mapper can recognise them without extras:

**Media**: `date`, `title`, `type`, `genre`, `description`
**Commerce**: `date`, `title`, `merchant`, `price`, `order_id`, `currency`
**Travel**: `date`, `title`, `fare`, `pickup`, `dropoff`, `destination`, `origin`, `currency`

Unrecognised field names are packed into `additional_metadata` and still
stored — they're not lost.
