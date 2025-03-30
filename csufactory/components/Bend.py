class Pdk(BaseModel):
    """Store layers, cross_sections, cell functions, simulation_settings ...

    only one Pdk can be active at a given time.

    Parameters:
        name: PDK name.
        version: PDK version.
        cross_sections: dict of cross_sections factories.
        cells: dict of parametric cells that return Components.
        models: dict of models names to functions.
        symbols: dict of symbols names to functions.
        default_symbol_factory:
        base_pdk: a pdk to copy from and extend.
        default_decorator: decorate all cells, if not otherwise defined on the cell.
        layers: maps name to gdslayer/datatype.
            For example dict(si=(1, 0), sin=(34, 0)).
        layer_stack: maps name to layer numbers, thickness, zmin, sidewall_angle.
            if can also contain material properties
            (refractive index, nonlinear coefficient, sheet resistance ...).
        layer_views: includes layer name to color, opacity and pattern.
        layer_transitions: transitions between different cross_sections.
        constants: dict of constants for the PDK.
        materials_index: material spec names to material spec, which can be:
            string: material name.
            float: refractive index.
            float, float: refractive index real and imaginary part.
            function: function of wavelength.
        routing_strategies: functions enabled to route.
        bend_points_distance: default points distance for bends in um.
        connectivity: defines connectivity between layers through vias.

    """

    name: str
    version: str = ""
    cross_sections: dict[str, CrossSectionFactory] = Field(
        default_factory=dict, exclude=True
    )
    cross_section_default_names: dict[str, str] = Field(
        default_factory=dict, exclude=True
    )
    cells: dict[str, ComponentFactory] = Field(default_factory=dict, exclude=True)
    models: dict[str, Callable] = Field(default_factory=dict, exclude=True)
    symbols: dict[str, ComponentFactory] = Field(default_factory=dict)
    default_symbol_factory: Callable[..., ComponentFactory] = Field(
        default=floorplan_with_block_letters, exclude=True
    )
    base_pdks: list[Pdk] = Field(default_factory=list)
    default_decorator: Callable[[Component], None] | None = Field(
        default=None, exclude=True
    )
    layers: type[LayerEnum] | None = None
    layer_stack: LayerStack | None = None
    layer_views: LayerViews | None = None
    layer_transitions: dict[LayerSpec | tuple[Layer, Layer], ComponentSpec] = Field(
        default_factory=dict
    )
    constants: dict[str, Any] = constants
    materials_index: dict[str, MaterialSpec] = Field(default_factory=dict)
    routing_strategies: RoutingStrategies | None = None
    bend_points_distance: float = 20 * nm
    connectivity: list[ConnectivitySpec] | None = None
    max_cellname_length: int = CONF.max_cellname_length

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="forbid",
    )