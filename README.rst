openSUSE Distribution Aliases
-----------------------------


This project provides a list of the currently maintained openSUSE
distributions. It is the openSUSE equivalent of `fedora-distro-aliases
<https://github.com/rpm-software-management/fedora-distro-aliases>`_.


Usage
=====

.. code-block:: python-console

   >>> from opensuse_distro_aliases import get_distro_aliases
   >>> aliases = get_distro_aliases()


Obtain the name and version of all currently active releases:

.. code-block:: python-console

   >>> [f"{d.name} {d.version}" for d in aliases["opensuse-all"]]
   ['openSUSE Leap 15.6', 'openSUSE Leap 15.5', 'openSUSE Leap Micro 6.0', 'openSUSE Leap Micro 5.5', 'openSUSE Tumbleweed 20240714']


Get the corresponding main development project in the `Open Build Service
<https://build.opensuse.org/>`_:

.. code-block:: python-console

   >>> [f"{d.name}: {d.obs_project_name}" for d in aliases["opensuse-all"]]
   ['openSUSE Leap: openSUSE:Leap:15.6', 'openSUSE Leap: openSUSE:Leap:15.5', 'openSUSE Leap Micro: openSUSE:Leap:Micro:6.0', 'openSUSE Leap Micro: openSUSE:Leap:Micro:5.5', 'openSUSE Tumbleweed: openSUSE:Factory']


The caveat of the function ``get_distro_aliases`` is that it performs network
calls, which can be slow, flaky or otherwise unavailable (e.g. in koji or OBS
builds). Since the openSUSE distribution releases are quite seldom, we provide
the pre-fetched result of ``get_distro_aliases`` as the constant
``CACHED_ACTIVE_DISTRIBUTION_ALIASES``. The only difference between the
pre-fetched and the fetched value should be the version of openSUSE Tumbleweed
(this version changes daily, but has otherwise little significance).
