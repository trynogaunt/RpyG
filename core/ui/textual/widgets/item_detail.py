"""Fiche d'objet (ItemDetailView) en markup Rich, partagée par les écrans inventaire et catalogue."""
from core.views.inventory_view import ItemDetailView

BAR_WIDTH = 10


def wear_bar(wear: float) -> str:
    filled = round(BAR_WIDTH * wear)
    style = "green" if wear > 0.6 else "#ffb000" if wear > 0.3 else "red"
    return f"[{style}]{'█' * filled}[/][dim]{'░' * (BAR_WIDTH - filled)}[/] {round(wear * 100)}%"


def slot_names(t, slots) -> str:
    return " + ".join(t(f"ui.inventory.slots.{s.value}") for s in slots)


def detail_markup(t, d: ItemDetailView) -> str:
    rows: list[tuple[str, str]] = []
    if d.category:
        rows.append((t("ui.inventory.details.category"), t(f"ui.inventory.categories.{d.category}")))
    if d.equipped_on:
        rows.append((t("ui.inventory.details.equipped_on"), slot_names(t, d.equipped_on)))
    elif d.slots:
        rows.append((t("ui.inventory.details.slots"),
                     f" {t('ui.inventory.details.or')} ".join(slot_names(t, c) for c in d.slots)))
    if d.quantity > 1:
        rows.append((t("ui.inventory.details.quantity"), f"×{d.quantity}"))
    if d.wear is not None:
        rows.append((t("ui.inventory.details.wear"), wear_bar(d.wear)))
    if d.attack:
        rows.append((t("ui.inventory.details.attack"), " · ".join([
            f"{t('ui.inventory.details.damage')} ×{d.attack.damage_multiplier:g}",
            f"{t('ui.inventory.details.crit')} ×{d.attack.crit_multiplier:g}",
            f"{t('ui.inventory.details.crit_chance')} {d.attack.crit_chance:.0%}",
            f"{t('ui.inventory.details.hits')} {d.attack.hits}",
        ])))
    if d.defense:
        rows.append((t("ui.inventory.details.defense"), " · ".join([
            f"{t('ui.inventory.details.armor')} ×{d.defense.armor_multiplier:g}",
            f"{t('ui.inventory.details.magic_resistance')} ×{d.defense.magic_resistance:g}",
            f"{t('ui.inventory.details.block_chance')} {d.defense.block_chance:.0%}",
        ])))

    width = max((len(label) for label, _ in rows), default=0)
    lines = [f"[italic]{t(f'items.{d.item_id}.description')}[/]", ""]
    lines += [f"[#ffb000]{label:<{width}}[/]  {value}" for label, value in rows]
    return "\n".join(lines)
