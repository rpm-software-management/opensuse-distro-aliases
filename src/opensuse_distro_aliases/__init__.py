import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Dict
from typing import List
from typing import Literal
from typing import Optional
from typing import TypedDict
from typing import Union

import requests

__all__ = ["Distro", "get_distro_aliases", "CACHED_ACTIVE_DISTRIBUTION_ALIASES"]


@dataclass(frozen=True)
class Distro:
    """An openSUSE distribution"""

    #: full name of the distribution
    name: str

    #: version number of this distribution
    version: str

    #: name-version of the distribution corresponding to the mock chroot
    namever: str

    #: main project on build.opensuse.org from which this distribution is built
    obs_project_name: Optional[str]

    #: flag whether this distribution is still under active maintenance
    active: bool = True


class _Release(TypedDict):
    name: str
    version: str


class _StableRelease(_Release):
    state: Literal["Stable", "EOL"]


def get_distro_aliases(include_eol: bool = False) -> Dict[str, List[Distro]]:
    """Fetches the currently maintained openSUSE distributions from
    get.opensuse.org and returns a dictionary of alias groups
    (e.g. `opensuse-leap-all`) as keys and the list of distros as values.

    """

    releases: Dict[str, List[Union[_Release, _StableRelease]]] = requests.get(
        "https://get.opensuse.org/api/v0/distributions.json"
    ).json()

    productlist = ET.fromstring(
        requests.get(
            "https://api.opensuse.org/public/source/openSUSE?view=productlist&expand=1&format=xml"
        ).text
    )

    res: Dict[str, List[Distro]] = {}

    for distro_name, distro_list in releases.items():
        aliases = []

        if distro_name == "LeapMicro":
            distro_name = "Leap-Micro"

        if distro_name == "Tumbleweed":
            d = distro_list[0]
            aliases.append(
                Distro(
                    name=d["name"],
                    version=d["version"],
                    namever="opensuse-tumbleweed",
                    obs_project_name="openSUSE:Factory",
                    active=True,
                )
            )

        else:
            matching_products = productlist.findall(f"product[@name='{distro_name}']")

            for distri in distro_list:
                if (active := distri.get("state", "") != "EOL") or include_eol:
                    version = distri["version"]
                    obs_project = [
                        op
                        for op in (
                            p.attrib.get("originproject", "") for p in matching_products
                        )
                        if op.endswith(version)
                    ]

                    aliases.append(
                        Distro(
                            name=(n := distri["name"]),
                            version=version,
                            # stay compatible with mock chroot names
                            namever=f"{n.lower().replace(' ', '-')}-{version}",
                            obs_project_name=obs_project[0] if obs_project else None,
                            active=active,
                        )
                    )

        if aliases:
            res[f"opensuse-{distro_name.lower()}-all"] = aliases

    opensuse_all = []
    for distros in res.values():
        opensuse_all.extend(distros)
    res["opensuse-all"] = opensuse_all

    return res


#: Cached openSUSE distribution aliases. Only includes distributions that are
#: active/maintained
#:
#: This constant is a pre-fetched result of :py:func:`get_distro_aliases` with
#: the only difference that the :py:attr:`Distro.version` of openSUSE Tumbleweed
#: is clipped.
#:
#: This constant is periodically updated and should be quite up to date most of
#: the time as most openSUSE releases don't change very often.
CACHED_ACTIVE_DISTRIBUTION_ALIASES: Dict[str, List[Distro]] = {
    "opensuse-leap-all": (
        _leap_all := [
            Distro(
                name="openSUSE Leap",
                version="16.0",
                namever="opensuse-leap-16.0",
                obs_project_name=None,
                active=True,
            ),
            Distro(
                name="openSUSE Leap",
                version="15.6",
                namever="opensuse-leap-15.6",
                obs_project_name="openSUSE:Leap:15.6",
            ),
            Distro(
                name="openSUSE Leap",
                version="15.5",
                namever="opensuse-leap-15.5",
                obs_project_name="openSUSE:Leap:15.5",
            ),
        ]
    ),
    "opensuse-leap-micro-all": (
        _leap_micro_all := [
            Distro(
                name="openSUSE Leap Micro",
                version="6.1",
                namever="opensuse-leap-micro-6.1",
                obs_project_name="openSUSE:Leap:Micro:6.1",
            ),
            Distro(
                name="openSUSE Leap Micro",
                version="6.0",
                namever="opensuse-leap-micro-6.0",
                obs_project_name="openSUSE:Leap:Micro:6.0",
            ),
            Distro(
                name="openSUSE Leap Micro",
                version="5.5",
                namever="opensuse-leap-micro-5.5",
                obs_project_name="openSUSE:Leap:Micro:5.5",
            ),
        ]
    ),
    "opensuse-tumbleweed-all": [
        _tw := Distro(
            name="openSUSE Tumbleweed",
            version="",
            namever="opensuse-tumbleweed",
            obs_project_name="openSUSE:Factory",
        )
    ],
    "opensuse-all": [*_leap_all, *_leap_micro_all, _tw],
}
