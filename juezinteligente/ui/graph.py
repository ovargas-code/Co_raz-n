import abc
import typing

from PySide2 import QtCore
from PySide2.QtCore import QRectF, QPointF, QRect, QPoint, Signal, Qt, QObject
from PySide2.QtGui import QWheelEvent, QPainter, QBrush, QPen, QFont, QFontMetrics, QPolygon, QPainterPath, QImage, QColor
from PySide2.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsItem, QStyleOptionGraphicsItem, \
    QWidget, QGraphicsSceneHoverEvent, QGraphicsSceneContextMenuEvent, QMenu, QGraphicsObject, QGraphicsPathItem, \
    QGraphicsSceneMouseEvent, QAction, QActionGroup
from dependency_injector.wiring import Provide

from juezinteligente.model.judge import NodePosition, Case
from juezinteligente.ui.constants import Constants
from juezinteligente.util import app_config, convert_data_to_color, split_string
from juezinteligente.util.containers import Container


class CaseView(QGraphicsView):
    """ The main view for the case graph representation

    Attributes:
        parent_window: QMainWindow that contains this view
        case: Case the case object that is rendered in this view
    """

    def __init__(self, parent, window, case: Case, constants: Constants = Provide[Container.constants]):
        super(CaseView, self).__init__(parent)
        self.parent_window = window
        self.case = case
        self.constants = constants
        self.initialize()

    def wheelEvent(self, event: QWheelEvent):
        """ See base class
        """

        # Here we use two modifiers for the event:
        # - alt: for zooming in and out
        # - ctrl: for horizontal scrolling
        # without modifiers it scrolls the view vertically
        modifiers = event.modifiers()
        if modifiers == Qt.AltModifier:
            self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

            in_factor = 1.15
            out_factor = 1 / in_factor

            if event.delta() > 0:
                zoom_factor = in_factor
            else:
                zoom_factor = out_factor

            self.scale(zoom_factor, zoom_factor)
        elif modifiers == Qt.ControlModifier:
            self.horizontalScrollBar().wheelEvent(event)
        else:
            super(CaseView, self).wheelEvent(event)

    def initialize(self):
        """ Initializes the view."""

        # Configure settings for view rendering and behaviour
        self.setRenderHint(QPainter.Antialiasing, True)
        self.setRenderHint(QPainter.TextAntialiasing, True)
        self.setRenderHint(QPainter.HighQualityAntialiasing, True)
        self.setRenderHint(QPainter.SmoothPixmapTransform, True)
        self.setRenderHint(QPainter.NonCosmeticDefaultPen, True)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.setDragMode(QGraphicsView.RubberBandDrag)

        # Create the scene that holds the nodes
        scene = CaseScene(self)
        scene.selectionChanged.connect(self.on_selection_changed)
        self.setScene(scene)
        self.setStyleSheet(app_config['tooltip_style'])

    def showEvent(self, event):
        super(CaseView, self).showEvent(event)
        root_nodes = [node for node in self.scene().nodes.values() if node.parent_node is None]
        if root_nodes:
            QtCore.QTimer.singleShot(100, lambda: self.centerOn(root_nodes[0]))

    def on_selection_changed(self):
        for node in self.scene().nodes.values():
            node.update()
        selected = self.scene().selectedItems()
        if len(selected) > 0:
            # Show properties of the first selected item
            selected_item = selected[0]
            self.parent_window.select_node(selected_item)
        else:
            self.parent_window.select_node()

    def create_node(self, node_type: type, model, parent_node=None, favorable=None):
        """ Creates a new node in the view

        Args:
            node_type: the type (class) of the node to be created
            model: the model object that holds the data for the node
            parent_node: Optional; node object that represents the parent of the new node
            favorable: Optional; bool that indicates if the node is created in the list a favorable children

        Returns:
            The node object that was created.
        """

        node_item = node_type(model=model, parent_node=parent_node)

        self.scene().nodes[model.name] = node_item

        connection = None

        # Add connection and children to parent_node
        if parent_node:
            if favorable:
                parent_node.fav_children.append(node_item)
                connection = ConnectionItem(parent_node.out_fav_plug, node_item.in_plug)
            else:
                parent_node.unfav_children.append(node_item)
                connection = ConnectionItem(parent_node.out_unfav_plug, node_item.in_plug)

        # Define node position:
        # If it is a new node (not loaded from repository)
        if not model.position:
            # If the node is the pretense (hypothesis) of the case
            if not parent_node:
                x = self.scene().sceneRect().center().x()
                y = self.scene().sceneRect().height() / 10
                position = QPointF(x, y)
                node_item.setPos(position)
                node_item.setPos(position - node_item.node_center)
            else:
                # Else calculate the position in reference to its parent node
                position = self.calculate_new_node_position(parent_node, favorable)
                node_item.setPos(position)
        else:
            # If it is a node loaded from the repository
            position = QPointF(model.position.x, model.position.y)
            node_item.setPos(position)

        self.scene().addItem(node_item)

        if connection is not None:
            connection.update_path()
            self.scene().addItem(connection)

        node_item.signal_new_fact_action_selected.connect(self.parent_window.on_new_fact_action_selected)
        node_item.signal_new_evidence_action_selected.connect(self.parent_window.on_new_evidence_action_selected)
        node_item.signal_delete_action_selected.connect(self.parent_window.on_delete_action_selected)
        node_item.signal_calculate_evidential_weight.connect(self.parent_window.on_calculate_evidential_weight)
        node_item.signal_ignore_node_action_selected.connect(self.parent_window.on_ignore_node_selected)

        # Update the position in the model so it can be saved
        pos = node_item.pos()
        node_item.model.position = NodePosition(x=pos.x(), y=pos.y())

        return node_item

    def delete_node(self, node):
        """ Deletes a node and all its children

        Args:
            node: Node object to be deleted
        """

        # Update the evidence counter (not sure if this is required)
        if type(node) is EvidenceNode:
            self.case.evidence_counter -= 1

        parent_node = node.parent_node
        parent_node.model.delete_child(node.model)

        # Get all the connections that have the node as source
        connections = filter(lambda item: isinstance(item, ConnectionItem) and item.source_plug.parentItem() == node,
                             self.scene().items())

        for conn in connections:
            self.delete_node(conn.target_plug.parentItem())
            self.scene().removeItem(conn)

        # Get all the connections that have the node as target
        in_conn = filter(lambda item: isinstance(item, ConnectionItem) and item.target_plug.parentItem() == node,
                         self.scene().items())
        for c in in_conn:
            self.scene().removeItem(c)

        parent_node.remove_child(node)
        self.scene().removeItem(node)

    def calculate_new_node_position(self, parent_node, favorable):
        """ Calculates the new node position based on it parent node. If the node is favorable it will put its position
        to the left of the parent according to the number of children that are also favorable. It is the same logic
        for the unfavorable nodes, but to the right of the parent.

        Args:
            parent_node: Node that represent the parent of the new node
            favorable: bool that indicates if the position is to the right or left of the parent node

        Returns:
            A QPointF indicating the position for the new node
        """

        ref_pos = parent_node.pos() + parent_node.node_center
        x = ref_pos.x()
        y = ref_pos.y() + parent_node.base_height/2
        margin = parent_node.base_width / 4
        if favorable:
            for _ in parent_node.fav_children:
                x -= (parent_node.base_width + margin)
        else:
            x += margin
            for _ in range(len(parent_node.unfav_children)-1):
                x += (parent_node.base_width + margin)

        return QPointF(x, y)

    def auto_layout(self):
        """ Automatically layouts all the nodes in the graph to avoid overlaps.
        We perform a post-order tree traversal to compute subtree contours and then
        position nodes bottom-up/top-down.
        """
        # Find the root node (usually a HypothesisNode, parent_node is None)
        root_nodes = [node for node in self.scene().nodes.values() if node.parent_node is None]
        if not root_nodes:
            return
        root = root_nodes[0]

        # Spacing parameters
        sibling_gap = 40.0
        parent_gap = 80.0
        vertical_gap = 280.0

        def layout_subtrees_side_by_side(layouts, sibling_gap):
            if not layouts:
                return [], [], []
            
            n = len(layouts)
            x_pos = [0.0] * n
            
            _, first_left, first_right = layouts[0]
            merged_left = list(first_left)
            merged_right = list(first_right)
            
            for i in range(1, n):
                _, c_left, c_right = layouts[i]
                
                # Find minimum shift to avoid overlap at all common depths
                shift = 0.0
                overlap_depth = min(len(merged_right), len(c_left))
                if overlap_depth > 0:
                    shift = max(merged_right[d] - c_left[d] + sibling_gap for d in range(overlap_depth))
                
                x_pos[i] = shift
                
                # Merge contours
                for d in range(max(len(merged_left), len(c_left))):
                    if d < len(merged_left) and d < len(c_left):
                        merged_left[d] = min(merged_left[d], c_left[d] + shift)
                        merged_right[d] = max(merged_right[d], c_right[d] + shift)
                    elif d >= len(merged_left):
                        merged_left.append(c_left[d] + shift)
                        merged_right.append(c_right[d] + shift)
            
            return x_pos, merged_left, merged_right

        def layout_node_local(node):
            w = node.base_width
            
            # If leaf node
            if not node.fav_children and not node.unfav_children:
                return {node: 0.0}, [-w / 2.0], [w / 2.0]
            
            offsets = {node: 0.0}
            
            if node == root:
                left_contour_left = []
                right_contour_left = []
                if node.fav_children:
                    left_layouts = []
                    for child in node.fav_children:
                        c_offsets, c_left, c_right = layout_node_local(child)
                        left_layouts.append((c_offsets, c_left, c_right))
                    
                    x_pos_left, merged_left_left, merged_right_left = layout_subtrees_side_by_side(left_layouts, sibling_gap)
                    
                    # Shift so that the rightmost edge of the entire left group is at -w/2.0 - parent_gap
                    max_left_prime = max(merged_right_left)
                    shift_left = (-w / 2.0 - parent_gap) - max_left_prime
                    
                    for i, child in enumerate(node.fav_children):
                        child_offsets = left_layouts[i][0]
                        child_center = x_pos_left[i] + shift_left
                        for n, off in child_offsets.items():
                            offsets[n] = child_center + off
                    
                    left_contour_left = [val + shift_left for val in merged_left_left]
                    right_contour_left = [val + shift_left for val in merged_right_left]
                
                left_contour_right = []
                right_contour_right = []
                if node.unfav_children:
                    right_layouts = []
                    for child in node.unfav_children:
                        c_offsets, c_left, c_right = layout_node_local(child)
                        right_layouts.append((c_offsets, c_left, c_right))
                    
                    x_pos_right, merged_left_right, merged_right_right = layout_subtrees_side_by_side(right_layouts, sibling_gap)
                    
                    # Shift so that the leftmost edge of the entire right group is at w/2.0 + parent_gap
                    min_right_prime = min(merged_left_right)
                    shift_right = (w / 2.0 + parent_gap) - min_right_prime
                    
                    for i, child in enumerate(node.unfav_children):
                        child_offsets = right_layouts[i][0]
                        child_center = x_pos_right[i] + shift_right
                        for n, off in child_offsets.items():
                            offsets[n] = child_center + off
                    
                    left_contour_right = [val + shift_right for val in merged_left_right]
                    right_contour_right = [val + shift_right for val in merged_right_right]
                
                # Merge contours for root
                left_contour = [-w / 2.0]
                right_contour = [w / 2.0]
                
                max_depth = max(len(left_contour_left), len(left_contour_right))
                for d in range(max_depth):
                    left_vals = []
                    right_vals = []
                    if d < len(left_contour_left):
                        left_vals.append(left_contour_left[d])
                        right_vals.append(right_contour_left[d])
                    if d < len(left_contour_right):
                        left_vals.append(left_contour_right[d])
                        right_vals.append(right_contour_right[d])
                    left_contour.append(min(left_vals))
                    right_contour.append(max(right_vals))
                
                return offsets, left_contour, right_contour
            
            else:
                children = node.fav_children + node.unfav_children
                child_layouts = []
                for child in children:
                    c_offsets, c_left, c_right = layout_node_local(child)
                    child_layouts.append((c_offsets, c_left, c_right))
                
                x_pos, merged_left, merged_right = layout_subtrees_side_by_side(child_layouts, sibling_gap)
                
                # Center the immediate children under the parent
                midpoint = (x_pos[0] + x_pos[-1]) / 2.0
                shift = -midpoint
                
                for i, child in enumerate(children):
                    child_offsets = child_layouts[i][0]
                    child_center = x_pos[i] + shift
                    for n, off in child_offsets.items():
                        offsets[n] = child_center + off
                
                left_contour_shifted = [val + shift for val in merged_left]
                right_contour_shifted = [val + shift for val in merged_right]
                
                left_contour = [-w / 2.0] + left_contour_shifted
                right_contour = [w / 2.0] + right_contour_shifted
                
                return offsets, left_contour, right_contour

        # Compute relative offsets, starting at root.
        offsets, _, _ = layout_node_local(root)

        # Set vertical coordinates based on node depth
        depths = {}
        def compute_depths(node, current_depth):
            depths[node] = current_depth
            for child in node.fav_children + node.unfav_children:
                compute_depths(child, current_depth + 1)
        compute_depths(root, 0)

        # Root position references
        root_current_cx = root.pos().x() + root.base_width / 2.0
        root_current_y = root.pos().y()
        if root_current_y == 0.0 and root_current_cx == root.base_width / 2.0:
            root_current_cx = self.width() / 2.0 if self.width() > 0 else 500.0
            root_current_y = 50.0

        # Apply computed positions to all nodes
        for node, x_offset in offsets.items():
            node_cx = root_current_cx + x_offset
            node_x = node_cx - node.base_width / 2.0
            node_y = root_current_y + depths[node] * vertical_gap
            node.setPos(QPointF(node_x, node_y))
            # Also update model position
            node.model.position = NodePosition(x=node_x, y=node_y)

        # Update connection paths in the scene
        self.scene().updateScene()

        # Center view on root node to ensure it is nicely organized on screen
        self.centerOn(root)
        QtCore.QTimer.singleShot(50, lambda: self.centerOn(root))



class CaseScene(QGraphicsScene):
    """ This is the scene contained in the view. It holds a dictionary of all the nodes that are added and
    has a method to update the connection constantly

    Attributes:
        _brush: A QBrush to be used in rendering
        nodes: dictionary with the nodes in the scene
    """

    def __init__(self, parent):
        super(CaseScene, self).__init__(parent)

        self._brush = None
        self.nodes = dict()

    def drawBackground(self, painter: QPainter, rect: QRectF):
        self._brush = QBrush()
        self._brush.setStyle(QtCore.Qt.SolidPattern)
        self._brush.setColor(convert_data_to_color(app_config['bg_color']))

        painter.fillRect(rect, self._brush)

    def updateScene(self):
        for connection in [i for i in self.items() if isinstance(i, ConnectionItem)]:
            connection.update_path()


class NodeItem(QGraphicsObject):
    """ This class represents the abstraction of the types of Nodes that can be added to the view

    Attributes:
        parent_node: The parent of this object
        text: str that contains the text that is shown in the tooltip of the node
        label: str that contains the text that is rendered in the node label
        pre_selected: bool that indicates
        fav_children: list of favorable children nodes
        unfav_children: list of unfavorable children nodes

    Signals:
        signal_new_fact_action_selected: Signal emitted when add fact action is selected in the node context menu
        signal_new_evidence_action_selected: Signal emitted when add evidence action is clicked in the node context menu
        signal_delete_action_selected: Signal emitted when delete action is clicked in the node context menu
        signal_calculate_evidential_weight: Signal emitted when calculate evidential weight action is clicked in the
                                            node context menu
        signal_ignore_node_action_selected: Signal emitted when ignore action is clicked in the node context menu
    """

    signal_new_fact_action_selected = Signal(object)
    signal_new_evidence_action_selected = Signal(object)
    signal_delete_action_selected = Signal(object)
    signal_calculate_evidential_weight = Signal(object)
    signal_ignore_node_action_selected = Signal(object)

    def __init__(self, text, label, parent_node, constants: Constants = Provide[Container.constants]):
        super(NodeItem, self).__init__()

        self.constants = constants
        self.PROBABILITY_MENU_ACTIONS = [self.constants.UNSUPPORTED, self.constants.UNLIKELY, self.constants.LIKELY,
                                    self.constants.MOST_LIKELY, self.constants.VERY_LIKELY, self.constants.ALMOST_TRUE,
                                    self.constants.TRUE]

        self.setZValue(1)
        self.parent_node = parent_node
        self.text = text
        self.label = label
        self.pre_selected = False
        self.fav_children = list()
        self.unfav_children = list()

        self.setToolTip(self.text)

        self._new_fact_action = None
        self._new_evidence_action = None
        self._edit_node_action = None
        self._delete_node_action = None
        self._assign_credibility_action = None
        self._relevance_action = None
        self._calculate_evidential_weight_action = None
        self._ignore_node_action = None

        self._create_style()

    def itemChange(self, change, value):
        """ See base class """

        # In this case only the change in position is of interest
        # because we need to update the model with the new position
        if change == QGraphicsItem.ItemPositionChange:
            if self.model.position is not None:
                self.model.position.x = value.x()
                self.model.position.y = value.y()
            else:
                self.model.position = NodePosition(x=value.x(), y=value.y())

        return super(NodeItem, self).itemChange(change, value)

    def remove_child(self, child_node):
        """ Remove a child node from this object

        Args:
            child_node: Node to be removed
        """

        if child_node in self.fav_children:
            self.fav_children.remove(child_node)
        elif child_node in self.unfav_children:
            self.unfav_children.remove(child_node)

    def _create_style(self):
        """ Creates the style that is used to render the node

        It reads the values from a configuration file a set several instanve variables to be used later
        """

        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsScenePositionChanges, True)

        # Dimensions
        self.base_width = app_config['node']['width']
        self.base_height = app_config['node']['height']
        self.border = app_config['node']['border']
        self.radius = app_config['node']['radius']
        self.fav_width = app_config['node']['fav_width']
        self.fav_height = app_config['node']['fav_height']
        self.attr_width = app_config['node']['attr_width']
        self.attr_height = app_config['node']['attr_height']

        self.node_center = QPointF()
        self.node_center.setX(self.base_width / 2.0)
        self.node_center.setY(self.base_height / 5.0 * 4)

        fav_x = self.node_center.x() - self.radius - self.fav_width
        self.fav_center = QPointF(fav_x, self.node_center.y())

        unfav_x = self.node_center.x() + self.radius + self.fav_width
        self.unfav_center = QPointF(unfav_x, self.node_center.y())

        self._brush = QBrush()
        self._brush.setStyle(QtCore.Qt.SolidPattern)
        self._brush.setColor(convert_data_to_color(app_config['node']['bg_color']))

        # Determine class prefix for specific border colors
        cls_name = self.__class__.__name__
        if cls_name == "HypothesisNode":
            prefix = "pretense_"
        elif cls_name == "FactNode":
            prefix = "fact_"
        elif cls_name == "EvidenceNode":
            prefix = "evidence_"
        else:
            prefix = ""

        # Set specific border pens
        self._normal_border_pen = QPen()
        self._normal_border_pen.setStyle(QtCore.Qt.SolidLine)
        self._normal_border_pen.setWidth(self.border)
        self._normal_border_pen.setColor(convert_data_to_color(app_config['node'].get(f"{prefix}border_color", app_config['node']['border_color'])))

        self._hover_border_pen = QPen()
        self._hover_border_pen.setStyle(QtCore.Qt.SolidLine)
        self._hover_border_pen.setWidth(self.border + 1)
        self._hover_border_pen.setColor(convert_data_to_color(app_config['node'].get(f"{prefix}border_hover", app_config['node']['selected_rect_color'])))

        self._selected_border_pen = QPen()
        self._selected_border_pen.setStyle(QtCore.Qt.SolidLine)
        self._selected_border_pen.setWidth(self.border + 2)
        self._selected_border_pen.setColor(convert_data_to_color(app_config['node'].get(f"{prefix}border_selected", app_config['node']['selected_rect_color'])))

        self._pen = self._normal_border_pen
        self._pen_sel = self._selected_border_pen

        self._bounding_rect_pen = self._normal_border_pen
        self._bounding_rect_pre_selected_pen = self._hover_border_pen
        self._bounding_rect_selected_pen = self._selected_border_pen

        self._text_pen = QPen()
        self._text_pen.setStyle(QtCore.Qt.SolidLine)
        self._text_pen.setColor(convert_data_to_color(app_config['node']['text_color']))

        self._node_text_font = QFont(app_config['node']['text_font'], app_config['node']['text_size'], QFont.Bold)

        self._fav_pen = QPen()
        self._fav_pen.setStyle(QtCore.Qt.SolidLine)
        self._fav_pen.setColor(convert_data_to_color(app_config['node']['fav_border_color']))
        self._fav_pen.setWidth(self.border)

        self._unfav_pen = QPen()
        self._unfav_pen.setStyle(QtCore.Qt.SolidLine)
        self._unfav_pen.setColor(convert_data_to_color(app_config['node']['unfav_border_color']))
        self._unfav_pen.setWidth(self.border)

        self._relevance_pen = QPen()
        self._relevance_pen.setStyle(QtCore.Qt.SolidLine)
        self._relevance_pen.setColor(convert_data_to_color(app_config['node']['relevance_color']))
        self._relevance_pen.setWidth(self.border)

        self._lower_attr_pen = QPen()
        self._lower_attr_pen.setWidth(self.border)

    @abc.abstractmethod
    def _paint_lower_attributes(self, painter: QPainter, option: QStyleOptionGraphicsItem):
        """ This abstract method renders the lower attribute of the node (credibility or probatory weight).
        It is intended to be implemented by sub classes

        Args:
            painter: QPainter object use to paint
            option: Graphics options
        """

        raise NotImplementedError

    @abc.abstractmethod
    def _paint_relevance_attributes(self, painter: QPainter, option: QStyleOptionGraphicsItem):
        """ This abstract method renders the relevance attribute of the node.
        It is intended to be implemented by sub classes

        Args:
            painter: QPainter object use to paint
            option: Graphics options
        """

        raise NotImplementedError
    
    @abc.abstractmethod
    def _paint_label(self, painter: QPainter, option: QStyleOptionGraphicsItem):
        """ This abstract method renders node's label. It is intended to be implemented by sub classes

        Args:
            painter: QPainter object use to paint
            option: Graphics options
        """

        raise NotImplementedError

    @abc.abstractmethod
    def _paint_rect_bg(self, painter: QPainter, option: QStyleOptionGraphicsItem, rect: QRect):
        """ This abstract method paint the background rectangle of the node.
        It is intended to be implemented by sub classes

        Args:
            painter: QPainter object use to paint
            option: Graphics options
        """

        raise NotImplementedError

    def _paint_node_base(self, painter: QPainter, option: QStyleOptionGraphicsItem):
        """ Sets the pen and brush for the outline and the label of the nodes

        Args:
            painter: QPainter object use to paint
            option: Graphics options
        """
        painter.setBrush(self._brush)
        painter.setPen(self._pen)

        # Node label
        painter.setPen(self._text_pen)
        painter.setFont(self._node_text_font)

    def _paint_favorable_plug(self, painter: QPainter, option: QStyleOptionGraphicsItem):
        """ Paints the plug where favorable children are connected to

        Args:
            painter: QPainter object use to paint
            option: Graphics options
        """

        brush = QBrush()
        brush.setColor(convert_data_to_color(app_config['node']['fav_bg_color']))
        brush.setStyle(Qt.SolidPattern)
        rect = QRect(self.fav_center.x() - self.fav_width / 2,
                     self.fav_center.y() - self.fav_height / 2,
                     self.fav_width,
                     self.fav_height)
        painter.setBrush(brush)
        painter.setPen(self._fav_pen)
        painter.drawEllipse(rect)

        metrics = QFontMetrics(painter.font())
        fav_text = "F"
        fav_text_width = metrics.boundingRect(fav_text).width()
        fav_text_height = metrics.boundingRect(fav_text).height()
        fav_text_rect = QtCore.QRect(self.fav_center.x() - fav_text_width / 2,
                                     self.fav_center.y() - fav_text_height / 2,
                                     fav_text_width,
                                     fav_text_height)
        # Use white text for legibility
        text_pen = QPen(convert_data_to_color(app_config['node']['attr_text_color']))
        painter.setPen(text_pen)
        painter.drawText(fav_text_rect, QtCore.Qt.AlignCenter, fav_text)

    def _paint_unfavorable_plug(self, painter: QPainter, option: QStyleOptionGraphicsItem):
        """ Paints the plug where unfavorable children are connected to

        Args:
            painter: QPainter object use to paint
            option: Graphics options
        """

        painter.setPen(self._unfav_pen)
        brush = QBrush()
        brush.setColor(convert_data_to_color(app_config['node']['unfav_bg_color']))
        brush.setStyle(Qt.SolidPattern)
        painter.setBrush(brush)
        rect = QRect(self.unfav_center.x() - self.fav_width / 2,
                     self.unfav_center.y() - self.fav_height / 2,
                     self.fav_width,
                     self.fav_height)
        painter.drawEllipse(rect)
        metrics = QFontMetrics(painter.font())
        unfav_text = app_config['node']['unfav_text']
        unfav_text_width = metrics.boundingRect(unfav_text).width()
        unfav_text_height = metrics.boundingRect(unfav_text).height()
        unfav_text_rect = QtCore.QRect(self.unfav_center.x() - unfav_text_width / 2,
                                       self.unfav_center.y() - unfav_text_height / 2,
                                       unfav_text_width,
                                       unfav_text_height)
        # Use white text for legibility
        text_pen = QPen(convert_data_to_color(app_config['node']['attr_text_color']))
        painter.setPen(text_pen)
        painter.drawText(unfav_text_rect, QtCore.Qt.AlignCenter, unfav_text)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: typing.Optional[QWidget] = ...):
        """ See base class."""
        rect = self.boundingRect()

        # Paint the rounded background
        self._paint_rect_bg(painter, option, rect)

        # Draw the card border outline
        if self.isSelected():
            painter.setPen(self._selected_border_pen)
        elif self.pre_selected:
            painter.setPen(self._hover_border_pen)
        else:
            painter.setPen(self._normal_border_pen)

        painter.setBrush(QtCore.Qt.NoBrush)
        border_width = painter.pen().widthF()
        adjusted_rect = rect.adjusted(border_width / 2.0, border_width / 2.0, -border_width / 2.0, -border_width / 2.0)
        painter.drawRoundedRect(adjusted_rect, 12.0, 12.0)

        # Node base
        self._paint_node_base(painter, option)

        # Node favorable plug
        self._paint_favorable_plug(painter, option)

        # Node unfavorable plug
        self._paint_unfavorable_plug(painter, option)
        
        self._paint_label(painter, option)

        # Node relevance attribute
        self._paint_relevance_attributes(painter, option)

        # Node lower attribute could be either credibility or probative value (weight)
        self._paint_lower_attributes(painter, option)

    def boundingRect(self):
        """ See base class. """

        rect = QRect(0, 0, self.base_width, self.base_height)
        rect = QRectF(rect)
        return rect

    def hoverEnterEvent(self, event: QGraphicsSceneHoverEvent):
        self.pre_selected = True
        super(NodeItem, self).hoverEnterEvent(event)

    def hoverLeaveEvent(self, event: QGraphicsSceneHoverEvent):
        self.pre_selected = False
        super(NodeItem, self).hoverLeaveEvent(event)

    @abc.abstractmethod
    def _add_own_menu_actions(self, context_menu: QMenu):
        """ This is abstract method is intended to be implemented by sub classes so they can
        add its own actions to the context menu when right clicked

        Args:
            context_menu: QMenu in which the action are going to be added
        """
        
        raise NotImplementedError

    # noinspection PyUnresolvedReferences
    def contextMenuEvent(self, event: QGraphicsSceneContextMenuEvent):
        view = self.scene().views()[0]
        context_menu = QMenu(view)

        self._add_own_menu_actions(context_menu)

        action: QAction = context_menu.exec_(event.screenPos())

        if action is not None:
            if action == self._new_fact_action:
                self.signal_new_fact_action_selected.emit(self)
            elif action == self._new_evidence_action:
                self.signal_new_evidence_action_selected.emit(self)
            elif action == self._delete_node_action:
                self.signal_delete_action_selected.emit(self)
            elif action == self._calculate_evidential_weight_action:
                self.signal_calculate_evidential_weight.emit(self)
            elif action == self._ignore_node_action:
                self.signal_ignore_node_action_selected.emit(self)

        super(NodeItem, self).contextMenuEvent(event)

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent):
        self.scene().updateScene()
        super(NodeItem, self).mouseMoveEvent(event)


class NodeWithRelevance(NodeItem):

    def __init__(self, text, label, parent_node):
        super(NodeWithRelevance, self).__init__(text, label, parent_node)
        self.base_height = app_config['node']['child_height']
        self.node_center.setY(self.base_height / 6.0 * 5.2)
        fav_x = self.node_center.x() - self.radius - self.fav_width
        self.fav_center = QPointF(fav_x, self.node_center.y())
        unfav_x = self.node_center.x() + self.radius + self.fav_width
        self.unfav_center = QPointF(unfav_x, self.node_center.y())
        self.in_plug = InPlugItem(self)

    def _paint_label(self, painter: QPainter, option: QStyleOptionGraphicsItem):
        text = split_string(self.model.label, 19)

        font: QFont = painter.font()
        new_font: QFont = font.__copy__()
        metrics = QFontMetrics(font)

        text_height = metrics.boundingRect(text).height()

        y = self.node_center.y() - (self.attr_height * 7)
        rect = QRect(self.node_center.x() - self.attr_width / 2 - 5,
                     y, self.attr_width + 11, self.attr_height + text_height + 9)

        text_pen = QPen()
        text_pen.setColor(convert_data_to_color(app_config['node']['attr_text_color']))
        new_font.setPointSize(11)
        painter.setFont(new_font)
        painter.setPen(text_pen)
        painter.drawText(rect, QtCore.Qt.AlignCenter, text)
        painter.setFont(font)

    @abc.abstractmethod
    def _paint_lower_attributes(self, painter: QPainter, option: QStyleOptionGraphicsItem):
        pass

    @abc.abstractmethod
    def _relevance_label(self):
        pass

    def _paint_relevance_attributes(self, painter: QPainter, option: QStyleOptionGraphicsItem):
        brush = QBrush()
        brush.setColor(convert_data_to_color(app_config['node']['relevance_color']))
        brush.setStyle(Qt.SolidPattern)
        metrics = QFontMetrics(painter.font())
        label_text = self._relevance_label()
        text_width = metrics.boundingRect(label_text).width()
        text_height = metrics.boundingRect(label_text).height()
        x = self.node_center.x() - text_width / 2
        y = self.node_center.y() - (self.radius + self.attr_height + text_height) * 1.8
        text_rect = QRect(x, y, text_width, text_height)

        # Draw header text with soft slate color
        header_pen = QPen(QColor(203, 213, 225))
        painter.setPen(header_pen)
        painter.drawText(text_rect, QtCore.Qt.AlignCenter, label_text)

        rect = QRect(self.node_center.x() - self.attr_width / 2,
                     y + text_height, self.attr_width, self.attr_height)
        painter.setBrush(brush)
        painter.setPen(self._relevance_pen)
        painter.drawRoundedRect(rect, 6, 6)

        if not self.model.relevance:
            text = self.constants.UNASSIGNED
        else:
            text = self.model.relevance

        text_pen = QPen()
        text_pen.setColor(convert_data_to_color(app_config['node']['attr_text_color']))
        painter.setPen(text_pen)
        painter.drawText(rect, QtCore.Qt.AlignCenter, text)

    def update_relevance(self, action: QAction):
        self.model.relevance = action.text()
        self.update()

    def _paint_node_base(self, painter: QPainter, option: QStyleOptionGraphicsItem):
        if self.model.ignored:
            self.setOpacity(0.5)
        else:
            self.setOpacity(1)

        super()._paint_node_base(painter, option)
        self.update()


class HypothesisNode(NodeItem):

    def __init__(self, model, parent_node):
        super(HypothesisNode, self).__init__(model.desc, model.name, parent_node)
        self.model = model
        self.out_fav_plug = OutFavPlugItem(self)
        self.out_unfav_plug = OutUnfavPlugItem(self)

    def _paint_node_base(self, painter: QPainter, option: QStyleOptionGraphicsItem):
        super()._paint_node_base(painter, option)
        image = QImage(":/images/img/hypothesis.png")
        img_point = QPointF(self.node_center.x() - image.width() / 2,
                            self.node_center.y() - image.height() / 2 + 5)

        painter.drawImage(img_point, image)

    def _paint_label(self, painter: QPainter, option: QStyleOptionGraphicsItem):
        text = split_string(self.model.label, 19)

        font: QFont = painter.font()
        new_font: QFont = font.__copy__()
        metrics = QFontMetrics(font)

        text_height = metrics.boundingRect(text).height()

        y = self.node_center.y() - (self.radius + self.attr_height + text_height) * 1.8
        rect = QRect(self.node_center.x() - self.attr_width / 2 - 5,
                     y, self.attr_width + 11, self.attr_height + text_height + 3)
        
        text_pen = QPen()
        text_pen.setColor(convert_data_to_color(app_config['node']['attr_text_color']))
        new_font.setPointSize(11)
        painter.setFont(new_font)
        painter.setPen(text_pen)
        painter.drawText(rect, QtCore.Qt.AlignCenter, text)
        painter.setFont(font)
    
    def _paint_relevance_attributes(self, painter: QPainter, option: QStyleOptionGraphicsItem):
        self._relevance_pen.setColor(convert_data_to_color(app_config['node']['pretense_attr_color']))
        brush = QBrush()
        brush.setColor(convert_data_to_color(app_config['node']['pretense_attr_color']))
        brush.setStyle(Qt.SolidPattern)
        x = self.node_center.x() - self.attr_width / 2
        y = self.node_center.y() - self.attr_height * 2

        metrics = QFontMetrics(painter.font())
        label_text = self.constants.PROBATORY_WEIGHT_LABEL  # app_config['node']['calculated_attr_label']
        text_width = metrics.boundingRect(label_text).width()
        text_height = metrics.boundingRect(label_text).height()
        text_rect = QRect(self.node_center.x() - text_width / 2, y - text_height, text_width, text_height)
        
        # Soft slate header
        header_pen = QPen(QColor(203, 213, 225))
        painter.setPen(header_pen)
        painter.drawText(text_rect, QtCore.Qt.AlignCenter, label_text)

        rect = QRect(x, y, self.attr_width, self.attr_height)
        painter.setBrush(brush)
        painter.setPen(self._relevance_pen)
        painter.drawRoundedRect(rect, 6, 6)

        if not self.model.probatory_weight:
            text = self.constants.NOT_YET_CALCULATED
        else:
            text = self.model.probatory_weight

        text_pen = QPen()
        text_pen.setColor(convert_data_to_color(app_config['node']['attr_text_color']))
        painter.setPen(text_pen)
        painter.drawText(rect, QtCore.Qt.AlignCenter, text)

    def _paint_lower_attributes(self, painter: QPainter, option: QStyleOptionGraphicsItem):
        """
        This method in not implemented because an hypothesis node does not need a lower attribute

        :param painter:
        :param option:
        :return:
        """
        pass

    def _paint_rect_bg(self, painter: QPainter, option: QStyleOptionGraphicsItem, rect: QRectF):
        brush = QBrush(convert_data_to_color(app_config['node']['pretense_bg_color']))
        painter.setBrush(brush)
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawRoundedRect(rect, 12.0, 12.0)

    def _add_own_menu_actions(self, context_menu: QMenu):
        self._new_fact_action = context_menu.addAction(self.constants.ADD_FACT)
        context_menu.addSeparator()
        self._calculate_evidential_weight_action = context_menu.addAction(self.constants.CALCULATE_PROBATORY_WEIGHT)


class EvidenceNode(NodeWithRelevance):

    def __init__(self, model, parent_node):
        super(EvidenceNode, self).__init__(model.desc, model.name, parent_node)
        self.out_fav_plug = None
        self.out_unfav_plug = None
        self.model = model

    def _paint_node_base(self, painter: QPainter, option: QStyleOptionGraphicsItem):
        super()._paint_node_base(painter, option)
        image = QImage(":/images/img/evidence.png")
        img_point = QPointF(self.node_center.x() - image.width() / 2,
                            self.node_center.y() - image.height() / 2 + 5)

        painter.drawImage(img_point, image)

    def _paint_rect_bg(self, painter: QPainter, option: QStyleOptionGraphicsItem, rect: QRectF):
        brush = QBrush(convert_data_to_color(app_config['node']['evidence_bg_color']))
        painter.setBrush(brush)
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawRoundedRect(rect, 12.0, 12.0)

    def _relevance_label(self):
        return self.constants.PERTINENCE  # app_config['node']['pertinence_label']

    def _paint_lower_attributes(self, painter: QPainter, option: QStyleOptionGraphicsItem):
        self._lower_attr_pen.setColor(convert_data_to_color(app_config['node']['credibility_color']))
        brush = QBrush()
        brush.setColor(convert_data_to_color(app_config['node']['credibility_color']))
        brush.setStyle(Qt.SolidPattern)
        x = self.node_center.x() - self.attr_width / 2
        y = self.node_center.y() - self.attr_height * 2

        metrics = QFontMetrics(painter.font())
        label_text = self.constants.CREDIBILITY  # ['node']['credibility_label']
        text_width = metrics.boundingRect(label_text).width()
        text_height = metrics.boundingRect(label_text).height()
        text_rect = QRect(self.node_center.x() - text_width / 2, y - text_height, text_width, text_height)
        
        # Soft slate header
        header_pen = QPen(QColor(203, 213, 225))
        painter.setPen(header_pen)
        painter.drawText(text_rect, QtCore.Qt.AlignCenter, label_text)

        rect = QRect(x, y, self.attr_width, self.attr_height)
        painter.setBrush(brush)
        painter.setPen(self._lower_attr_pen)
        painter.drawRoundedRect(rect, 6, 6)

        if not self.model.credibility:
            text = self.constants.UNASSIGNED
        else:
            text = self.model.credibility

        text_pen = QPen()
        text_pen.setColor(convert_data_to_color(app_config['node']['attr_text_color']))
        painter.setPen(text_pen)
        painter.drawText(rect, QtCore.Qt.AlignCenter, text)

    def _add_own_menu_actions(self, context_menu: QMenu):

        relevance_menu = context_menu.addMenu(self.constants.PERTINENCE)
        relevance_action_group = QActionGroup(relevance_menu)
        for a in self.PROBABILITY_MENU_ACTIONS:
            action = relevance_action_group.addAction(a)
            action.setCheckable(True)
            relevance_menu.addAction(action)
            if self.model.relevance == a:
                action.setChecked(True)
        relevance_action_group.triggered.connect(self.update_relevance)

        credibility_menu = context_menu.addMenu(self.constants.CREDIBILITY)
        credibility_action_group = QActionGroup(credibility_menu)
        for a in self.PROBABILITY_MENU_ACTIONS:
            action = credibility_action_group.addAction(a)
            action.setCheckable(True)
            credibility_menu.addAction(action)
            if self.model.credibility == a:
                action.setChecked(True)
        credibility_action_group.triggered.connect(self.update_credibility)

        context_menu.addSeparator()
        self._ignore_node_action = context_menu.addAction(self.constants.IGNORE)
        self._ignore_node_action.setCheckable(True)
        if self.model.ignored:
            self._ignore_node_action.setChecked(True)
        context_menu.addSeparator()
        self._delete_node_action = context_menu.addAction(self.constants.DELETE)

    def update_credibility(self, action: QAction):
        self.model.credibility = action.text()
        self.update()

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: typing.Optional[QWidget] = ...):
        super().paint(painter, option, widget)

    def _paint_favorable_plug(self, painter: QPainter, option: QStyleOptionGraphicsItem):
        """
        This method overrides the parent logic because an evidence node does not need
        the favorable and unfavorable plugs
        """
        pass

    def _paint_unfavorable_plug(self, painter: QPainter, option: QStyleOptionGraphicsItem):
        """
        This method overrides the parent logic because an evidence node does not need
        the favorable and unfavorable plugs
        """
        pass


class FactNode(NodeWithRelevance):
    def __init__(self, model, parent_node):
        super(FactNode, self).__init__(model.desc, model.name, parent_node)
        self.model = model
        self.out_fav_plug = OutFavPlugItem(self)
        self.out_unfav_plug = OutUnfavPlugItem(self)

    def _paint_node_base(self, painter: QPainter, option: QStyleOptionGraphicsItem):
        super()._paint_node_base(painter, option)
        image = QImage(":/images/img/fact.png")
        img_point = QPointF(self.node_center.x() - image.width()/2,
                            self.node_center.y() - image.height()/2 + 5)

        painter.drawImage(img_point, image)

    def _paint_rect_bg(self, painter: QPainter, option: QStyleOptionGraphicsItem, rect: QRectF):
        brush = QBrush(convert_data_to_color(app_config['node']['fact_bg_color']))
        painter.setBrush(brush)
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawRoundedRect(rect, 12.0, 12.0)

    def _relevance_label(self):
        return self.constants.RELEVANCE  # app_config['node']['relevance_label']

    def _paint_lower_attributes(self, painter: QPainter, option: QStyleOptionGraphicsItem):
        self._lower_attr_pen.setColor(convert_data_to_color(app_config['node']['pretense_attr_color']))
        brush = QBrush()
        brush.setColor(convert_data_to_color(app_config['node']['pretense_attr_color']))
        brush.setStyle(Qt.SolidPattern)
        x = self.node_center.x() - self.attr_width / 2
        y = self.node_center.y() - self.attr_height * 2

        metrics = QFontMetrics(painter.font())
        label_text = self.constants.PROBATORY_WEIGHT_LABEL  # app_config['node']['calculated_attr_label']
        text_width = metrics.boundingRect(label_text).width()
        text_height = metrics.boundingRect(label_text).height()
        text_rect = QRect(self.node_center.x() - text_width / 2, y - text_height, text_width, text_height)
        
        # Soft slate header
        header_pen = QPen(QColor(203, 213, 225))
        painter.setPen(header_pen)
        painter.drawText(text_rect, QtCore.Qt.AlignCenter, label_text)

        rect = QRect(x, y, self.attr_width, self.attr_height)
        painter.setBrush(brush)
        painter.setPen(self._lower_attr_pen)
        painter.drawRoundedRect(rect, 6, 6)


        if not self.model.probatory_weight:
            text = self.constants.NOT_YET_CALCULATED
        else:
            text = self.model.probatory_weight

        text_pen = QPen()
        text_pen.setColor(convert_data_to_color(app_config['node']['attr_text_color']))
        painter.setPen(text_pen)
        painter.drawText(rect, QtCore.Qt.AlignCenter, text)

    def _add_own_menu_actions(self, context_menu: QMenu):
        self._new_fact_action = context_menu.addAction(self.constants.ADD_SUB_FACT)
        self._new_evidence_action = context_menu.addAction(self.constants.ADD_EVIDENCE)
        context_menu.addSeparator()
        relevance_menu = context_menu.addMenu(self.constants.RELEVANCE)
        action_group = QActionGroup(relevance_menu)
        for a in self.PROBABILITY_MENU_ACTIONS:
            action = action_group.addAction(a)
            action.setCheckable(True)
            relevance_menu.addAction(action)
            if self.model.relevance == a:
                action.setChecked(True)
        action_group.triggered.connect(self.update_relevance)
        self._calculate_evidential_weight_action = context_menu.addAction(self.constants.CALCULATE_PROBATORY_WEIGHT)

        context_menu.addSeparator()
        self._ignore_node_action = context_menu.addAction(self.constants.IGNORE)
        self._ignore_node_action.setCheckable(True)
        if self.model.ignored:
            self._ignore_node_action.setChecked(True)
        context_menu.addSeparator()
        self._delete_node_action = context_menu.addAction(self.constants.DELETE)


class PlugItem(QGraphicsItem):

    def __init__(self, parent):
        super(PlugItem, self).__init__(parent)

        self.brush = QBrush()
        self.brush.setStyle(QtCore.Qt.SolidPattern)
        self.brush.setColor(convert_data_to_color(app_config['node']['plug_bg_color']))
        self.pen = QPen()
        self.pen.setStyle(QtCore.Qt.SolidLine)
        self.pen.setColor(convert_data_to_color(app_config['node']['plug_bg_color']))
        self.pen.setWidth(app_config['node']['plug_border_width'])

        self.connected_plugs = list()
        self.connections = list()

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: typing.Optional[QWidget] = ...):
        painter.setBrush(self.brush)
        painter.setPen(self.pen)
        painter.drawEllipse(self.boundingRect())


class InPlugItem(PlugItem):

    def __init__(self, parent):
        super(InPlugItem, self).__init__(parent)

    def boundingRect(self) -> QRectF:
        parent_rect = self.parentItem().boundingRect()
        width = height = parent_rect.width() / 14

        x = (parent_rect.width() - width) / 2
        y = int(-height / 2)

        rect = QRectF(QRect(x, y, width, height))

        return rect


class OutFavPlugItem(PlugItem):

    def __init__(self, parent):
        super(OutFavPlugItem, self).__init__(parent)

    def boundingRect(self) -> QRectF:
        width = height = self.parentItem().fav_width / 3
        x = self.parentItem().fav_center.x() - width/2
        y = self.parentItem().fav_center.y() + self.parentItem().fav_width/2 - height/2

        rect = QRectF(QRect(x, y, width, height))

        return rect


class OutUnfavPlugItem(PlugItem):

    def __init__(self, parent):
        super(OutUnfavPlugItem, self).__init__(parent)

    def boundingRect(self) -> QRectF:
        width = height = self.parentItem().fav_width / 3
        x = self.parentItem().unfav_center.x() - width / 2
        y = self.parentItem().unfav_center.y() + self.parentItem().fav_width / 2 - height / 2

        rect = QRectF(QRect(x, y, width, height))

        return rect


class ConnectionItem(QGraphicsPathItem):

    def __init__(self, source_plug, target_plug):
        super(ConnectionItem, self).__init__()

        self.setZValue(1)

        self.source_plug = source_plug
        self.target_plug = target_plug

        self._pen = QPen()
        self._pen.setColor(convert_data_to_color(app_config['node']['connection_color']))
        self._pen.setWidth(app_config['node']['connection_width'])

    def _calculate_target_and_source_points(self):
        source_plug_pos = self.source_plug.boundingRect().center()
        target_plug_pos = self.target_plug.boundingRect().center()
        parent_source_pos = self.source_plug.parentItem().pos()
        parent_target_pos = self.target_plug.parentItem().pos()

        source_x = parent_source_pos.x() + source_plug_pos.x()
        source_y = parent_source_pos.y() + source_plug_pos.y()

        target_x = parent_target_pos.x() + target_plug_pos.x()
        target_y = parent_target_pos.y() + target_plug_pos.y()

        self._source_point = QPointF(QPoint(source_x, source_y))
        self._target_point = QPointF(QPoint(target_x, target_y))

    def update_path(self):
        self._calculate_target_and_source_points()

        self.setPen(self._pen)

        path = QPainterPath()
        path.moveTo(self._source_point)
        dx = (self._target_point.x() - self._source_point.x()) * 0.5
        dy = self._target_point.y() - self._source_point.y()
        ctrl1 = QPointF(self._source_point.x() + dx, self._source_point.y() + dy * 1)
        ctrl2 = QPointF(self._source_point.x() + dx, self._source_point.y() + dy * 0)
        path.cubicTo(ctrl1, ctrl2, self._target_point)
        self.setPath(path)
