#!/usr/bin/env python

import citadel.nodes.node
import citadel.tools


class Webhook(citadel.nodes.node.Base):
    """:synopsis: Runs an HTTP client against the given URLs.

    :requirements: None
    :platform: Any

    **Usage**

    .. code-block:: yaml
        :linenos:

        webhook:
          - http://my.company.slack/notify/user&message=done

    While meant to be further developed into a more robust and fully fledged
    notification mechanism, it currently provides basic functionality for
    basic HTTP/S calls. The above example would result in the following:

    .. code-block:: bash
        :linenos:

        DOWNLOADER=""
        if which curl ; then
            DOWNLOADER="$(which curl) -O -s"
        elif which wget ; then
            DOWNLOADER="$(which wget) -q"
        else
            echo "Unable to find any downloader software. Aborting..." && exit 1
        fi
        $DOWNLOADER http://my.company.slack/notify/user&message
    """

    def __init__(self, yml, path):
        super(Webhook, self).__init__(yml, path)

        curl_exec = citadel.tools.get_executable('curl')
        self.output.append(citadel.tools.find_downloader())
        for url in yml:
            self.output.append('$DOWNLOADER ' + url)
