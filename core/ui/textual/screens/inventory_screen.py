from rich.text import Text
from textual import events, on
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Footer, OptionList, Static
from textual.widgets.option_list import Option

from core.game.actions import CloseInventory, EquipItem, InspectEquipped, InspectItem, UnequipItem
from core.game.response import Message
from core.items.base import Slot
from core.ui.textual.screens.base_screen import BaseScreen
from core.views.inventory_view import InventoryView, ItemDetailView

BAR_WIDTH = 10


def wear_bar(wear: float) -> str:
    filled = round(BAR_WIDTH * wear)
    style = "green" if wear > 0.6 else "#ffb000" if wear > 0.3 else "red"
    return f"[{style}]{'█' * filled}[/][dim]{'░' * (BAR_WIDTH - filled)}[/] {round(wear * 100)}%"


class InventoryList(OptionList):
    """Un clic (gauche ou droit) surligne l'objet et affiche sa fiche, sans l'équiper : seule Entrée agit."""

    async def _on_click(self, event: events.Click) -> None:
        event.prevent_default()                # sinon OptionList._on_click s'exécute aussi et sélectionne
        clicked = event.style.meta.get("option")
        if clicked is not None and not self.get_option_at_index(clicked).disabled:
            self.highlighted = clicked


class InventoryScreen(BaseScreen):
    """Trois panneaux : équipement, sac, fiche de l'objet surligné (mise à jour en direct)."""

    BINDINGS = [
        Binding("escape,i", "close", "ui.common.back"),
        Binding("tab", "app.focus_next", "ui.inventory.switch_panel"),
    ]

    def __init__(self, view: InventoryView | None = None, **kwargs):
        super().__init__(view=view, **kwargs)
        self.view = view
        self._signatures: dict[str, tuple] = {}
        self._keys: dict[str, list] = {"inv-equipment": [], "inv-bag": []}
        self._last_inspected = None
        self._button_actions: dict[str, object] = {}
        self._generation = 0                   # remove_children() est asynchrone : ids uniques par génération

    def compose(self):
        with Horizontal(id="inv-main"):
            with Vertical(id="inv-equipment-panel", classes="panel"):
                yield InventoryList(id="inv-equipment", classes="inv-list")
            with Vertical(id="inv-bag-panel", classes="panel"):
                yield InventoryList(id="inv-bag", classes="inv-list")
            with Vertical(id="inv-detail-panel", classes="panel"):
                yield Static(id="inv-detail")
                yield Vertical(id="inv-actions")
        yield Footer()

    # ----- rendu -----

    def update_view(self, view: InventoryView) -> None:
        self.view = view                       # appelé par BaseScreen.on_mount, une fois les widgets composés
        t = self.app.t
        used = sum(1 for c in view.cases if c.item_id is not None)
        self.query_one("#inv-equipment-panel").border_title = t("ui.inventory.equipment")
        self.query_one("#inv-bag-panel").border_title = f"{t('ui.inventory.bag')}  {used}/{len(view.cases)}"

        rebuilt = self._fill("inv-equipment", *self._equipment_options())
        rebuilt |= self._fill("inv-bag", *self._bag_options())
        if rebuilt:
            self._last_inspected = None        # les mêmes positions peuvent désigner d'autres objets
        self._render_detail(view.selected)
        if view.selected is None:
            self.call_after_refresh(self._inspect_focused)

    def _equipment_options(self) -> tuple[list[Text], list[Slot]]:
        t = self.app.t
        labels = {e.slot: t(f"ui.inventory.slots.{e.slot.value}") for e in self.view.equipment}
        width = max(len(label) for label in labels.values())
        prompts, keys = [], []
        for entry in self.view.equipment:
            label = f"[#ffb000]{labels[entry.slot]:<{width}}[/]  "
            if entry.item_id is None:
                label += f"[dim]{t('ui.inventory.empty')}[/]"
            else:
                label += f"[bold]{self._item_name(entry.item_id)}[/]"
            prompts.append(Text.from_markup(label))
            keys.append(entry.slot)
        return prompts, keys

    def _bag_options(self) -> tuple[list[Text], list[int]]:
        occupied = [(i, c) for i, c in enumerate(self.view.cases) if c.item_id is not None]
        if not occupied:
            return [Text.from_markup(f"[dim]{self.app.t('ui.inventory.empty_bag')}[/]")], [None]
        names = {i: self._item_name(c.item_id) + (f" ×{c.quantity}" if c.quantity > 1 else "") for i, c in occupied}
        width = max(len(n) for n in names.values())
        prompts, keys = [], []
        for i, case in occupied:
            label = f"{names[i]:<{width}}"
            if case.wear is not None:
                label += f"  {wear_bar(case.wear)}"
            prompts.append(Text.from_markup(label))
            keys.append(i)
        return prompts, keys

    def _fill(self, list_id: str, prompts: list[Text], keys: list) -> bool:
        """Remplit la liste seulement si son contenu a changé, en gardant la position du curseur."""
        signature = tuple(p.plain for p in prompts)
        if self._signatures.get(list_id) == signature:
            return False
        self._signatures[list_id] = signature
        self._keys[list_id] = keys
        lst = self.query_one(f"#{list_id}", OptionList)
        with self.prevent(OptionList.OptionHighlighted):
            previous = lst.highlighted
            lst.clear_options()
            lst.add_options([Option(p, disabled=k is None) for p, k in zip(prompts, keys)])
            if keys and keys[0] is not None:
                lst.highlighted = min(previous or 0, len(keys) - 1)
        return True

    def _render_detail(self, d: ItemDetailView | None) -> None:
        t = self.app.t
        panel = self.query_one("#inv-detail-panel")
        detail = self.query_one("#inv-detail", Static)
        if d is None:
            panel.border_title = t("ui.inventory.title")
            detail.update(f"[dim]{t('ui.inventory.hint_textual')}[/]")
            self._set_actions([])
            return

        panel.border_title = self._item_name(d.item_id)
        rows: list[tuple[str, str]] = []
        if d.category:
            rows.append((t("ui.inventory.details.category"), t(f"ui.inventory.categories.{d.category}")))
        if d.equipped_on:
            rows.append((t("ui.inventory.details.equipped_on"), self._slot_names(d.equipped_on)))
        elif d.slots:
            rows.append((t("ui.inventory.details.slots"),
                         f" {t('ui.inventory.details.or')} ".join(self._slot_names(c) for c in d.slots)))
        if d.quantity > 1:
            rows.append((t("ui.inventory.details.quantity"), f"×{d.quantity}"))
        if d.wear is not None:
            rows.append((t("ui.inventory.details.wear"), wear_bar(d.wear)))
        if d.attack:
            rows.append((t("ui.inventory.details.attack"), " · ".join([
                f"{t('ui.inventory.details.damage')} ×{d.attack.damage_multiplier:g}",
                f"{t('ui.inventory.details.crit')} ×{d.attack.crit_multiplier:g}",
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
        detail.update("\n".join(lines))

        actions = []
        if d.can_equip:
            for combo in d.slots:
                label = t("ui.inventory.equip_on", slot=self._slot_names(combo)) if len(d.slots) > 1 \
                    else t("ui.inventory.equip", item=self._item_name(d.item_id))
                actions.append((label + self._replaces(combo), EquipItem(d.index, combo), "primary"))
        if d.can_unequip:
            actions.append((t("ui.inventory.unequip", item=self._item_name(d.item_id)),
                            UnequipItem(d.equipped_on[0]), "warning"))
        self._set_actions(actions)

    def _set_actions(self, actions: list[tuple[str, object, str]]) -> None:
        signature = tuple((label, action) for label, action, _ in actions)
        if self._signatures.get("actions") == signature:
            return
        self._signatures["actions"] = signature
        box = self.query_one("#inv-actions", Vertical)
        box.remove_children()
        self._button_actions = {}
        self._generation += 1
        buttons = []
        for i, (label, action, variant) in enumerate(actions):
            button_id = f"inv-action-{self._generation}-{i}"
            self._button_actions[button_id] = action
            buttons.append(Button(label, id=button_id, variant=variant))
        box.mount(*buttons)

    def _replaces(self, combo) -> str:
        worn = {e.slot: e.item_id for e in self.view.equipment if e.item_id is not None}
        names = list(dict.fromkeys(self._item_name(worn[s]) for s in combo if s in worn))
        return f" ({self.app.t('ui.inventory.replaces', item=', '.join(names))})" if names else ""

    def _slot_names(self, slots) -> str:
        return " + ".join(self.app.t(f"ui.inventory.slots.{s.value}") for s in slots)

    def _item_name(self, item_id: str) -> str:
        return self.app.t(f"items.{item_id}.name")

    # ----- navigation -----

    def _inspect(self, list_id: str, index: int | None) -> None:
        keys = self._keys.get(list_id, [])
        if index is None or not 0 <= index < len(keys) or keys[index] is None:
            return
        target = (list_id, keys[index])
        if target == self._last_inspected:
            return
        self._last_inspected = target
        action = InspectEquipped(keys[index]) if list_id == "inv-equipment" else InspectItem(keys[index])
        self.app.dispatch(action)

    def _inspect_focused(self) -> None:
        focused = self.focused
        if isinstance(focused, OptionList):
            self._inspect(focused.id, focused.highlighted)

    @on(OptionList.OptionHighlighted)
    def _on_highlighted(self, event: OptionList.OptionHighlighted) -> None:
        self._inspect(event.option_list.id, event.option_index)

    def on_descendant_focus(self, event) -> None:
        if isinstance(event.widget, OptionList):
            self._inspect(event.widget.id, event.widget.highlighted)

    @on(OptionList.OptionSelected)
    def _on_selected(self, event: OptionList.OptionSelected) -> None:
        """Entrée : action principale de l'objet (premier emplacement libre, ou retirer)."""
        d = self.view.selected
        if d is None:
            return
        if d.can_unequip:
            self.app.dispatch(UnequipItem(d.equipped_on[0]))
        elif d.can_equip:
            self.app.dispatch(EquipItem(d.index))

    @on(Button.Pressed)
    def _on_button(self, event: Button.Pressed) -> None:
        action = self._button_actions.get(event.button.id)
        if action is not None:
            self.app.dispatch(action)

    def action_close(self) -> None:
        self.app.dispatch(CloseInventory())

    def show_messages(self, messages: tuple[Message, ...]) -> None:
        for message in messages:
            self.app.notify(self.app.resolve_message(self.app.translation, message), severity="warning")
