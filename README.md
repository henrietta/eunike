__eunike__ is both a text message gateway and a set of modules enabling to send different types of those with different hosts.

It is primarily constructed as a reliable SMS gateway with an GSM AT modem as execution device.

__eunike__ can be set up to work with different OAM (Order Acquisition Module) and OXM (Order Execution Module), so that messages to send can come from different sources and be sent by different means. As long as message is representable as a Python variable, there is no limit to what can be sent.

It is very easy to write custom OAM and OXM's. __eunike__ takes care of retrying deliveries, priority handling and routing messages to right OXM's. It also takes care of syncing messages to disk on shutdown, and reading them on startup. __eunike__ also provides advanced statistics for reviewing sending.

See COPYING for license.

# Parts

__OAM__ is a module that injects messages into the system. It collects it from different sources - HTTP interfaces, plain text files, whatever given module is written to support.

__OXM__ is a module that allows sending messages of given type. It handles sending messages and reporting that given source has failed, which will allow __eunike__ to retry with another module.

__OSM__ is a module that handles statistics, logging sent messages and provides an interface to analyze the statistical output.

__OPM__ is a module that handles presentation of the statistics.