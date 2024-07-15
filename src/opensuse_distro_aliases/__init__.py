import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Dict
from typing import List
from typing import Literal
from typing import TypedDict
from typing import Union

import requests

__all__ = ["Distro", "get_distro_aliases"]


@dataclass
class Distro:
    """An openSUSE distribution"""

    #: full name of the distribution
    name: str

    #: version number of this distribution
    version: str

    #: name-version of the distribution corresponding to the mock chroot
    namever: str

    #: main project on build.opensuse.org from which this distribution is built
    obs_project_name: str | None


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
                )
            )

        else:
            matching_products = productlist.findall(f"product[@name='{distro_name}']")

            for distri in distro_list:
                if include_eol or distri.get("state", "") != "EOL":
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
                        )
                    )

        if aliases:
            res[f"opensuse-{distro_name.lower()}-all"] = aliases

    opensuse_all = []
    for distros in res.values():
        opensuse_all.extend(distros)
    res["opensuse-all"] = opensuse_all

    return res
