__eunike__ is both a text message gateway and a set of modules enabling to send different types of those with different hosts.

It is primarily constructed as a reliable SMS gateway with an GSM AT modem as execution device.

__eunike__ can be set up to work with different OAM (Order Acquisition Module) and OXM (Order Execution Module), so that messages to send can come from different sources and be sent by different means. As long as message is representable as a Python variable, there is no limit to what can be sent.

It is very easy to write custom OAM and OXM's. __eunike__ takes care of retrying deliveries, priority handling and routing messages to right OXM's. It also takes care of syncing messages to disk on shutdown, and reading them on startup. __eunike__ also provides advanced statistics for reviewing sending.

See COPYING for license.