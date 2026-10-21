from core.enums import Screens
from core.updater import UpdateError, UpdateStatus, UpdateState, apply
from core.game.response import GameResponse, Message
from core.game.actions import (
    StartCombat,
    AttackEnemy,
    Flee,
    CloseCatalog,
    OpenCatalog,
    UseItem,
    ChooseStarter,
    CloseInventory,
    InspectItem,
    InspectEquipped,
    EquipItem,
    UnequipItem,
    OpenInventory,
    Action,
    NewGame,
    Quit,
    SetName,
    AllocatePoints,
    ConfirmCreation,
    Move,
    Explore,
    LoadGame,
    SaveGame,
    OpenSlots,
    SelectSlot,
    DeleteSave,
    ConfirmDelete,
    Back,
    Options,
    SetLocale,
    ApplyUpdate,
    InspectCatalogItem,
)
from core.enums import Direction
from core.game.creation import CreationState
from core.game.rules import CREATION_POINTS, STARTER_WEAPONS
from core.game.player import Player
from core.world.loader import World, RoomRef
from core.world.models import EncounterRef, WorldState
from core.views.base_view import BaseView
from core.views.exploration_view import EncounterView, ExplorationView
from core.views.catalog_view import CatalogView, ItemDetailView, CatalogEntryView
from core.views.option_view import OptionView
from core.views.slot_view import SlotsView
from core.game.text_keys import room_key
from core.errors import InvalidSave
from core.game.snapshot import GameSnapshot, PlayerSnapshot, BagEntry, EquippedEntry
from core.game.inventory import (
    Inventory,
    Equipped,
    InventoryError,
    InventoryFull,
    NotEquippable,
)
from core.items.catalog import ItemCatalog, UnknownItem
from core.enemies.catalog import EnemyCatalog
from core.combat.fighters import PlayerFighter
from core.combat.moves import Strike
from core.combat.state import CombatState, Outcome
from core.views.combat_view import CombatView, FoeView
from core.game.effect import EFFECTS
from core.items.base import Slot

from core.views.inventory_view import (
    InventoryView,
    InventorySlotView,
    EquipmentSlotView,
    ItemDetailView,
)

import logging
from collections import Counter
from random import Random

log = logging.getLogger(__name__)

UPDATE_ERROR_KEYS = {
    UpdateError.DIRTY: "ui.update.error.dirty",
    UpdateError.GIT_FAILED: "ui.update.error.git_failed",
    UpdateError.NOT_AVAILABLE: "ui.update.error.not_available",
}


class Game:
    def __init__(
        self,
        world: World | None = None,
        world_state: WorldState | None = None,
        settings=None,
        store=None,
        update=None,
        catalog: ItemCatalog | None = None,
        enemies: EnemyCatalog | None = None,
        dev: bool = False,
        rng: Random | None = None,
    ):
        self.screen: Screens | None = None
        self.creation: CreationState | None = None
        self.player: Player | None = None
        self.settings = {}
        self.world: World = world
        self.world_state: WorldState = world_state or WorldState()
        self._messages: list[Message] = []
        self.store = store
        self.settings = settings
        self.update = update
        self.catalog: ItemCatalog = catalog or ItemCatalog()
        self.enemies: EnemyCatalog = enemies or EnemyCatalog()
        self.slot_mode: str = "load"
        self.selected_slot: int | None = None
        self.confirm_delete: bool = False
        self.inventory_selection: int | Slot | None = None
        self._previous_screen: Screens | None = None
        self._catalog_selection: str | None = None
        self.combat: CombatState | None = None
        self._fighting: EncounterRef | None = None     # rencontre en cours, notée vaincue à la victoire (sauf respawn)
        self.rng = rng or Random()       # injecté par les tests pour fixer les jets
        self.restart_requested: bool = (
            False  # lu par main.py après la fermeture de l'interface
        )
        self.dev = dev

    def start(self) -> GameResponse:
        self.screen = Screens.MAIN_MENU

        return GameResponse(screen=self.screen)

    def _starter_choices(self) -> tuple[str, ...]:
        return tuple(item_id for item_id in STARTER_WEAPONS if item_id in self.catalog)

    def _move_player(self, direction: Direction) -> None:
        next_room = self.world.exit_from(self.player.location, direction)
        if next_room:
            self.player.location = next_room

    def _build_to_view(self) -> BaseView | None:
        match self.screen:
            case Screens.CREATION:
                return self.creation.to_view()
            case Screens.EXPLORATION:
                return self._exploration_to_view()
            case Screens.SLOTS:
                return self._slots_to_view(mode=self.slot_mode)
            case Screens.OPTIONS:
                return self._options_to_view()
            case Screens.INVENTORY:
                return self._inventory_to_view()
            case Screens.CATALOG:
                return self._catalog_to_view()
            case Screens.COMBAT:
                return self._combat_to_view()
            case _:
                return None

    def _catalog_to_view(self) -> CatalogView:
        items: list = []
        all_categories = self.catalog.categories()
        for c in all_categories:
            item_list = sorted(self.catalog.by_category(c), key=lambda item: item.id)
            for i in item_list:
                items.append(CatalogEntryView(i.id, c))
        return CatalogView(entries=tuple(items), selected=self._catalog_detail())

    def _catalog_detail(self) -> ItemDetailView | None:
        """Fiche de l'objet sélectionné : ni sac ni équipement, donc aucune action possible dessus."""
        if self._catalog_selection is None:
            return None
        item = self.catalog.get(self._catalog_selection)
        return ItemDetailView(
            item_id=item.id,
            category=item.category,
            attack=item.attack,
            defense=item.defense,
            slots=tuple(item.slots or ()),
            usable=item.usable,
        )
    
    def _exploration_to_view(self) -> ExplorationView:
        current_room = self.world.get_room(self.player.location)
        return ExplorationView(
            zone_id=self.player.location.zone_id,
            room_id=self.player.location.room_id,
            room_description=current_room.description,
            can_move={
                direction: self.world.exit_from(self.player.location, direction)
                is not None
                for direction in Direction
            },
            player_summary=self.player.to_summary(),
            encounters=tuple(EncounterView(id=e.id, enemies=tuple(Counter(e.enemies).items()))
                             for e in current_room.encounters
                             if EncounterRef(self.player.location, e.id) not in self.world_state.defeated),
        )

    def _combat_to_view(self) -> CombatView:
        foes = self.combat.foes
        ids = [f.enemy.id for f in foes]
        seen: dict[str, int] = {}
        views = []
        for foe in foes:
            tag = ""
            if ids.count(foe.enemy.id) > 1:            # deux rats : « Rat A », « Rat B »
                rank = seen.get(foe.enemy.id, 0)
                seen[foe.enemy.id] = rank + 1
                tag = chr(ord("A") + rank)
            views.append(FoeView(enemy_id=foe.enemy.id, health=foe.health, max_health=foe.enemy.max_health, tag=tag))
        return CombatView(
            foes=tuple(views),
            player_summary=self.player.to_summary(),
            log=tuple(self.combat.log),
        )

    def _options_to_view(self) -> OptionView:
        return OptionView(
            locale=self.settings.locale,
            available_locales=self.settings.available_locales,
            interface=self.settings.interface,
            available_interfaces=self.settings.available_interfaces,
            controls=self.settings.controls,
        )

    def _slots_to_view(self, mode: str) -> SlotsView:
        slots = self.store.list_slots_info() if self.store else ()
        selected = next((s for s in slots if s.slot == self.selected_slot), None)
        return SlotsView(
            slots=slots,
            mode=mode,
            selected=selected,
            confirm_delete=self.confirm_delete,
        )

    def _inventory_to_view(self) -> InventoryView:
        return InventoryView(
            cases=tuple(
                InventorySlotView(
                    item_id=c.item_id,
                    quantity=c.quantity,
                    wear=c.instance.wear if c.instance else None,
                    equippable=c.item_id in self.catalog
                    and self.catalog.get(c.item_id).equippable,
                )
                for c in self.player.inventory.cases
            ),
            equipment=tuple(
                EquipmentSlotView(
                    slot=e.slot,
                    item_id=e.item_id,
                    wear=e.instance.wear if e.instance else None,
                )
                for e in self.player.inventory.equipment
            ),
            selected=self._item_detail(),
        )

    def _item_detail(self) -> ItemDetailView | None:
        inventory = self.player.inventory
        selection = self.inventory_selection
        if isinstance(selection, Slot):
            equipped = inventory.occupant(selection)
            if equipped is None:
                return None
            instance, quantity, extra = (
                equipped.instance,
                1,
                {"equipped_on": equipped.slots},
            )
        elif selection is not None:
            case = inventory.cases[selection]
            if case.is_empty:
                return None
            instance, quantity, extra = (
                case.instance,
                case.quantity,
                {"index": selection},
            )
        else:
            return None

        item = (
            self.catalog.get(instance.item_id)
            if instance.item_id in self.catalog
            else None
        )
        return ItemDetailView(
            item_id=instance.item_id,
            quantity=quantity,
            wear=instance.wear,
            category=item.category if item else None,
            attack=item.attack if item else None,
            defense=item.defense if item else None,
            slots=tuple(item.slots or ()) if item else (),
            usable=item.usable if item else False,
            **extra,
        )

    def _explore_current_room(self) -> None:
        current_room = self.world.get_room(self.player.location)

        return Message(key="look_around", text="<text.messages.look_around>")

    def save_game(self, slot: int) -> None:
        log.info("Tentative de sauvegarde slot=%s", slot)
        if self.store is None or self.player is None:
            log.warning(
                "Sauvegarde annulée : store=%s player=%s", self.store, self.player
            )
            self._messages.append(Message(key="ui.messages.save_failed"))
            return
        try:
            self.store.save(slot, self.snapshot())
        except Exception as e:
            log.exception("Échec de la sauvegarde (slot %s)", slot)
            self._messages.append(Message(key="ui.messages.save_failed"))
            return
        self._messages.append(Message(key="ui.messages.game_saved"))

    def load_game(self, slot: int) -> None:
        if self.store is None:
            self._messages.append(Message(key="ui.messages.invalid_save"))
            return
        try:
            self.restore(self.store.load(slot))
        except InvalidSave:
            self._messages.append(Message(key="ui.messages.invalid_save"))
            return
        self._messages.append(Message(key="ui.messages.game_loaded"))

    def snapshot(self) -> GameSnapshot:
        p = self.player
        return GameSnapshot(
            player=PlayerSnapshot(
                name=p.name,
                health=p.health,
                level=p.level,
                xp=p.xp,
                allocated_points=tuple(
                    sorted(p.allocated_points.items(), key=lambda kv: kv[0].name)
                ),
                bag=tuple(
                    BagEntry(index=i, instance=c.instance, quantity=c.quantity)
                    for i, c in enumerate(p.inventory.cases)
                    if not c.is_empty
                ),
                equipped=tuple(
                    EquippedEntry(slots=e.slots, instance=e.instance)
                    for e in p.inventory.equipped
                ),
            ),
            location=p.location,
            explored=tuple(
                sorted(self.world_state.explored, key=lambda r: (r.zone_id, r.room_id))
            ),
            defeated=tuple(
                sorted(self.world_state.defeated,
                       key=lambda d: (d.room.zone_id, d.room.room_id, d.encounter_id))
            ),
        )

    def _check_room(self, ref: RoomRef) -> None:
        try:
            self.world.get_room(ref)
        except ValueError as e:
            raise InvalidSave(f"Salle inconnue : {ref}") from e

    def _check_item(self, item_id: str):
        try:
            return self.catalog.get(item_id)
        except UnknownItem as e:
            raise InvalidSave(f"Item inconnu : {item_id}") from e

    def _restore_inventory(self, snap: PlayerSnapshot) -> Inventory:
        inventory = Inventory()
        for entry in snap.bag:
            item = self._check_item(entry.instance.item_id)
            if (
                not 0 <= entry.index < inventory.size
                or not inventory.cases[entry.index].is_empty
            ):
                raise InvalidSave(f"Case d'inventaire invalide : {entry.index}")
            if not 1 <= entry.quantity <= item.max_stack:
                raise InvalidSave(
                    f"Quantité invalide pour {item.id} : {entry.quantity}"
                )
            case = inventory.cases[entry.index]
            case.instance, case.quantity = entry.instance, entry.quantity
        for entry in snap.equipped:
            item = self._check_item(entry.instance.item_id)
            if not item.equippable or entry.slots not in item.slots:
                raise InvalidSave(
                    f"{item.id} ne peut pas être équipé sur {entry.slots}"
                )
            if any(inventory.occupant(s) for s in entry.slots):
                raise InvalidSave(f"Slots déjà occupés : {entry.slots}")
            inventory.equipped.append(
                Equipped(slots=entry.slots, instance=entry.instance)
            )
        return inventory

    def restore(self, snap: GameSnapshot) -> None:
        self._check_room(snap.location)
        for ref in snap.explored:
            self._check_room(ref)
        for ref in snap.defeated:
            self._check_room(ref.room)
            if all(e.id != ref.encounter_id for e in self.world.get_room(ref.room).encounters):
                raise InvalidSave(f"Rencontre inconnue : {ref}")

        player = Player(name=snap.player.name)
        player.level = snap.player.level
        if snap.player.xp < 0:
            raise InvalidSave(f"XP invalide : {snap.player.xp}")
        player.xp = snap.player.xp
        player.allocated_points = dict(snap.player.allocated_points)
        if sum(player.allocated_points.values()) > CREATION_POINTS:
            raise InvalidSave("Points alloués incohérents")
        player.health = min(snap.player.health, player.max_health)
        player.location = snap.location
        player.inventory = self._restore_inventory(snap.player)

        self.player = player
        self.world_state.explored = set(snap.explored)
        self.world_state.defeated = set(snap.defeated)
        self.screen = Screens.EXPLORATION

    def handle_action(self, action: Action) -> GameResponse:
        self._messages.clear()
        match self.screen:
            case Screens.MAIN_MENU:
                self._handle_main_menu(action)
            case Screens.CREATION:
                self._handle_creation(action)
            case Screens.EXPLORATION:
                self._handle_exploration(action)
            case Screens.SLOTS:
                self._handle_slots(action)
            case Screens.OPTIONS:
                self._handle_options(action)
            case Screens.INVENTORY:
                self._handle_inventory(action)
            case Screens.CATALOG:
                self._handle_catalog(action)
            case Screens.COMBAT:
                self._handle_combat(action)
            case Screens.GAME_OVER:
                self._handle_game_over(action)
            case _:
                raise ValueError(f"Aucun handler pour l'écran : {self.screen}")
        view = self._build_to_view()
        return GameResponse(
            screen=self.screen, view=view, messages=tuple(self._messages)
        )

    def _handle_combat(self, action: Action) -> None:
        match action:
            case Flee():
                self._end_combat("ui.combat.fled")
            case AttackEnemy(target_index=target_index):
                if not self.combat.can_target(target_index):
                    return
                match self.combat.play_round(Strike(target_index), self.rng):
                    case Outcome.VICTORY:
                        if self._fighting is not None:
                            self.world_state.defeated.add(self._fighting)
                        xp = self.combat.xp_reward(self.player.level)
                        self._end_combat("ui.combat.victory")
                        self._grant_xp(xp)
                    case Outcome.DEFEAT:
                        self.combat = None
                        self.screen = Screens.GAME_OVER
                        self._messages.append(Message(key="ui.combat.defeat"))
            case _:
                raise ValueError(
                    f"Action inconnue : {action!r} (écran : {self.screen})"
                )

    def _grant_xp(self, xp: int) -> None:
        if not xp:
            return
        levels = self.player.gain_xp(xp)
        self._messages.append(Message(key="ui.combat.xp_gained", params={"xp": xp}))
        if levels:
            self._messages.append(Message(key="ui.combat.level_up", params={"level": self.player.level}))

    def _end_combat(self, message_key: str) -> None:
        self.combat = None
        self._fighting = None
        self.screen = Screens.EXPLORATION
        self._messages.append(Message(key=message_key))

    def _handle_game_over(self, action: Action) -> None:
        match action:
            case Quit() | Back():
                self.player = None
                self.screen = Screens.MAIN_MENU
            case _:
                raise ValueError(
                    f"Action inconnue : {action!r} (écran : {self.screen})"
                )

    def _handle_catalog(self, action: Action) -> None:
        match action:
            case InspectCatalogItem(item_id=item_id):
                if item_id in self.catalog:
                    self._catalog_selection = item_id
            case CloseCatalog():
                self.screen = Screens.MAIN_MENU
            case _:
                raise ValueError(
                    f"Action inconnue : {action!r} (écran : {self.screen})"
                )

    def _handle_main_menu(self, action: Action) -> None:
        match action:
            case NewGame():
                self.screen = Screens.CREATION
                self.creation = CreationState(starter_choices=self._starter_choices())
            case OpenSlots(mode=mode):
                self._open_slots(mode)
            case Options():
                self._previous_screen = self.screen
                self.screen = Screens.OPTIONS
            case Quit():
                self.screen = Screens.EXIT
            case ApplyUpdate():
                result = apply(self.update)
                if result.success and not result.deps_changed:
                    self.restart_requested = True
                    self.screen = Screens.EXIT
                elif result.success:
                    self._messages.append(Message(key="ui.update.success"))
                    self._messages.append(Message(key="ui.update.deps_changed"))
                    self._messages.append(Message(key="ui.update.restart"))
                    self.update = UpdateStatus(UpdateState.UP_TO_DATE)
                else:
                    self._messages.append(Message(key=UPDATE_ERROR_KEYS[result.error]))
            case OpenCatalog() if self.dev:
                self.screen = Screens.CATALOG
            case _:
                raise ValueError(
                    f"Action inconnue : {action!r} (écran : {self.screen})"
                )

    def _handle_creation(self, action: Action) -> None:
        match action:
            case SetName(name=name):
                self.creation.name = name.strip()
            case AllocatePoints(stat=stat, delta=1):
                if self.creation.can_add(stat):
                    self.creation.allocated_points[stat] += 1
            case AllocatePoints(stat=stat, delta=-1):
                if self.creation.can_remove(stat):
                    self.creation.allocated_points[stat] -= 1
            case ChooseStarter(item_id=item_id):
                if self.creation.can_choose(item_id):
                    self.creation.starter = item_id
            case ConfirmCreation():
                if self.creation.can_confirm():
                    self.player = Player(
                        name=self.creation.name,
                        allocated_points=self.creation.allocated_points,
                        location=self.world.start,
                    )
                    if self.creation.starter is not None:
                        starter = self.catalog.get(self.creation.starter)
                        self.player.inventory.add(
                            starter, instance=self.catalog.create(starter.id)
                        )
                    self.creation = None
                    self.world_state = WorldState()     # nouvelle partie : rien d'exploré ni de vaincu
                    self.screen = Screens.EXPLORATION
            case NewGame() | Quit():
                pass
            case _:
                raise ValueError(
                    f"Action inconnue : {action!r} (écran : {self.screen})"
                )

    def _handle_options(self, action: Action) -> None:
        match action:
            case SetLocale(locale=locale):
                if locale in self.settings.available_locales:
                    self.settings.locale = locale
                    self.settings.save()
            case Back():
                self.screen = self._previous_screen
            case _:
                raise ValueError(
                    f"Action inconnue : {action!r} (écran : {self.screen})"
                )

    def _handle_exploration(self, action: Action) -> None:
        match action:
            case Move(direction=direction):
                self._move_player(direction)
            case Explore():
                ref = self.player.location
                if ref in self.world_state.explored:
                    self._messages.append(Message(key="ui.messages.already_explored"))
                else:
                    self.world_state.explored.add(ref)
                    self._messages.append(
                        Message(
                            key=room_key(ref, "look_around"),
                            fallback_key="ui.messages.nothing_special",
                        )
                    )
            case OpenSlots(mode=mode):
                self._open_slots(mode)
            case OpenInventory():
                self._previous_screen = self.screen
                self.screen = Screens.INVENTORY
                self.inventory_selection = None
            case StartCombat(encounter_id=encounter_id):
                room = self.world.get_room(self.player.location)
                encounter = next((e for e in room.encounters if e.id == encounter_id), None)
                ref = EncounterRef(self.player.location, encounter_id)
                if encounter is not None and ref not in self.world_state.defeated:
                    # check_world_enemies garantit au chargement que chaque id existe dans le catalogue
                    self.combat = CombatState.start(PlayerFighter.from_player(self.player, self.catalog),
                                                      [self.enemies.get(i) for i in encounter.enemies])
                    self._fighting = None if encounter.respawn else ref
                    self.screen = Screens.COMBAT
            case Quit():
                self.screen = Screens.MAIN_MENU
            case _:
                raise ValueError(
                    f"Action inconnue : {action!r} (écran : {self.screen})"
                )

    def _handle_exit(self, action: Action) -> None:
        match action:
            case _:
                raise ValueError(
                    f"Action inconnue : {action!r} (écran : {self.screen})"
                )

    def _open_slots(self, mode: str) -> None:
        self._previous_screen = self.screen
        self.screen = Screens.SLOTS
        self.slot_mode = mode
        self.selected_slot = None
        self.confirm_delete = False

    def delete_save(self, slot: int) -> None:
        try:
            self.store.delete(slot)
        except OSError:
            log.exception("Échec de la suppression (slot %s)", slot)
            self._messages.append(Message(key="ui.messages.delete_failed"))
            return
        self._messages.append(Message(key="ui.messages.save_deleted"))

    def _handle_slots(self, action: Action) -> None:
        match action:
            case SelectSlot(slot=slot):
                self.selected_slot = slot
                self.confirm_delete = False
            case LoadGame(slot=slot):
                self.load_game(slot)
            case SaveGame(slot=slot):
                self.save_game(slot)
                self.screen = self._previous_screen
            case DeleteSave(slot=slot):
                self.selected_slot = slot
                self.confirm_delete = True
            case ConfirmDelete():
                if self.confirm_delete and self.selected_slot is not None:
                    self.delete_save(self.selected_slot)
                self.selected_slot = None
                self.confirm_delete = False
            case Back():
                if self.confirm_delete:
                    self.confirm_delete = False
                elif self.selected_slot is not None:
                    self.selected_slot = None
                else:
                    self.screen = self._previous_screen
            case _:
                raise ValueError(f"Action inconnue : {action}")

    def _handle_inventory(self, action: Action) -> None:
        match action:
            case InspectItem(index=index):
                cases = self.player.inventory.cases
                valid = 0 <= index < len(cases) and not cases[index].is_empty
                self.inventory_selection = index if valid else None
            case InspectEquipped(slot=slot):
                occupied = self.player.inventory.occupant(slot) is not None
                self.inventory_selection = slot if occupied else None
            case EquipItem(index=index, slots=slots):
                self._equip(index, slots)
                self.inventory_selection = None
            case UnequipItem(slot=slot):
                self._unequip(slot)
                self.inventory_selection = None
            case Back():
                if self.inventory_selection is not None:
                    self.inventory_selection = None
                else:
                    self.screen = self._previous_screen
            case UseItem(index=index):
                self._use_item(index)
                self.inventory_selection = None
            case CloseInventory():
                self.inventory_selection = None
                self.screen = self._previous_screen
            case _:
                raise ValueError(
                    f"Action inconnue : {action!r} (écran : {self.screen})"
                )

    def _equip(self, index: int, slots: tuple[Slot, ...] | None = None) -> None:
        inventory = self.player.inventory
        try:
            item_id = inventory.cases[index].item_id
            inventory.equip(index, self.catalog.get(item_id), slots)
        except InventoryFull:
            self._messages.append(Message(key="ui.inventory.messages.full"))
        except (NotEquippable, UnknownItem):
            self._messages.append(Message(key="ui.inventory.messages.cannot_equip"))
        except (InventoryError, IndexError):
            log.warning("Équipement impossible : case %s", index)

    def _unequip(self, slot) -> None:
        try:
            self.player.inventory.unequip(slot)
        except InventoryFull:
            self._messages.append(Message(key="ui.inventory.messages.full"))
        except InventoryError:
            log.warning("Rien à retirer sur %s", slot)

    def _use_item(self, index) -> None:
        inventory = self.player.inventory

        try:
            item_id = inventory.cases[index].item_id
            used_item = self.catalog.get(item_id)
            if not used_item.usable:
                return

            for u in used_item.on_use:
                EFFECTS[u.type](u.value, self.player)

        except KeyError:
            self._messages.append(Message(key="ui.inventory.messages.cannot_use"))
            log.warning("Effet inconnu pour l'objet %s", item_id)
        except (IndexError, UnknownItem):
            self._messages.append(Message(key="ui.inventory.messages.cannot_use"))
            log.warning("Impossible d'utiliser l'objet de la case %s", index)
        except InventoryError:
            self._messages.append(Message(key="ui.inventory.messages.cannot_use"))
            log.warning("Impossible d'utiliser l'objet de la case %s", index)
        else:
            inventory.take(index, 1)
            self._messages.append(Message(key="ui.inventory.messages.item_used"))
