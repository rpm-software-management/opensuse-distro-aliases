from typing import Set

from opensuse_distro_aliases import CACHED_ACTIVE_DISTRIBUTION_ALIASES
from opensuse_distro_aliases import Distro
from opensuse_distro_aliases import get_distro_aliases


def test_cache_up_to_date() -> None:
    # remove the version field from Tumbleweed, we don't want to precache that
    # value
    current_version = get_distro_aliases()
    for _, distros in current_version.items():
        for i, distri in enumerate(distros):
            if distri.name == "openSUSE Tumbleweed":
                kwargs = distri.__dict__
                kwargs["version"] = ""
                distros[i] = Distro(**kwargs)

    assert current_version == CACHED_ACTIVE_DISTRIBUTION_ALIASES


def test_distro_aliases_without_eol() -> None:
    for _, distros in get_distro_aliases(include_eol=False).items():
        for distri in distros:
            assert distri.active


def test_distro_aliases_with_eol_includes_all_active_ones() -> None:
    all_distris = get_distro_aliases(include_eol=True)
    active_distris = get_distro_aliases(include_eol=False)

    assert set(all_distris.keys()) == set(active_distris.keys())

    for distro_group in all_distris:
        cur_distro_group: Set[Distro] = set(all_distris[distro_group])
        active_distro_group: Set[Distro] = set(active_distris[distro_group])

        assert active_distro_group.issubset(cur_distro_group)

        for eol_distro in cur_distro_group.difference(active_distro_group):
            assert not eol_distro.active
