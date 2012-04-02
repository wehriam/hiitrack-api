HiiTrack
========

A funnel analysis platform built on Cassandra.

Overview
--------

HiiTrack associates events and properties with the visitors of a website or application, providing real-time reporting and analysis. It helps answer questions like, "What is the most effective version of my website's homepage?" or "What are common charateristics of my most valuable customers?"

Data is exposed via a REST-ful API and protected by basic HTTP authentication. HiiTrack is installed as a Python package and executed as a Twisted application. Protocol details such as compression and SSL are left to the user and trivially implemented via Nginx or similar software.

The paths used to interact with the API mirror the underlying data model, which includes the following:

* **User:** The account used to access HiiTrack data. The username forms the base path for all interaction. ``/exampleuser``
* **Bucket:** A collection of events, properties, and visitors. While bucket size is limited only by Cassandra's remarkable horizontal scalability, they should contain related events and properties. ``/exampleuser/homepagetestbucket``
* **Visitor:** A person or entity identified by a unique string. Often this is a UUID stored as a browser cookie.
* **Event:** An action associated with a visitor, for example a visit to a homepage. Events are timestamped and identified by a unique string. ``/exampleuser/homepagetestbucket/event/landed-on-homepage``
* **Property:** The name and value of a property associated with a visitor, for example "Homepage Version" + "Version A". ``/exampleuser/homepagetestbucket/property/homepage-version``
* **Funnel:** An ordered collection of events, and optionally a property, used to report aggregate behavior of visitors. For example events, "Landed on Homepage", "Created Account", and property "State or Province." This would return the count of users who landed on the homepage and subsequently created an account, segmented by state. ``/exampleuser/homepagetestbucket/funnel/signup-by-state``

Documentation
-------------

To follow! Please contact johnwehr@gmail.com if you have questions.

Installation
------------

``pip install https://github.com/hiidef/hiitrack-api/zipball/master``

