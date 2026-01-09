"""Plugin registries for dynamic component loading.

Registries allow implementations to register themselves at runtime.
"""

from typing import Any, Callable, Optional

from ..protocols import BasePlanner, BaseToolSelector

# Type aliases for factory functions
PlannerFactory = Callable[..., BasePlanner]
SelectorFactory = Callable[..., BaseToolSelector]


class PlannerRegistry:
    """Registry for planner implementations.
    
    Example:
        @PlannerRegistry.register("my_planner")
        class MyPlanner(BasePlanner):
            ...
        
        planner = PlannerRegistry.create("my_planner", config=...)
    """

    _registry: dict[str, PlannerFactory] = {}

    @classmethod
    def register(cls, name: str, factory: Optional[PlannerFactory] = None):
        """Register a planner implementation.
        
        Can be used as decorator or called directly.
        
        Args:
            name: Unique planner name
            factory: Factory function (class or callable)
        """
        def decorator(factory_fn: PlannerFactory) -> PlannerFactory:
            cls._registry[name] = factory_fn
            return factory_fn

        if factory is None:
            return decorator
        return decorator(factory)

    @classmethod
    def create(cls, name: str, *args, **kwargs) -> BasePlanner:
        """Create a planner instance by name.
        
        Args:
            name: Registered planner name
            *args, **kwargs: Arguments passed to factory
            
        Returns:
            Planner instance
            
        Raises:
            KeyError: If planner name not registered
        """
        if name not in cls._registry:
            available = ", ".join(cls._registry.keys())
            raise KeyError(
                f"Planner '{name}' not found. Available: {available}. "
                f"Install isage-agentic to get implementations."
            )
        return cls._registry[name](*args, **kwargs)

    @classmethod
    def list_planners(cls) -> list[str]:
        """List all registered planner names."""
        return list(cls._registry.keys())


class SelectorRegistry:
    """Registry for tool selector implementations.
    
    Example:
        @SelectorRegistry.register("my_selector")
        class MySelector(BaseToolSelector):
            ...
        
        selector = SelectorRegistry.create("my_selector", config=...)
    """

    _registry: dict[str, SelectorFactory] = {}

    @classmethod
    def register(cls, name: str, factory: Optional[SelectorFactory] = None):
        """Register a selector implementation.
        
        Can be used as decorator or called directly.
        
        Args:
            name: Unique selector name
            factory: Factory function (class or callable)
        """
        def decorator(factory_fn: SelectorFactory) -> SelectorFactory:
            cls._registry[name] = factory_fn
            return factory_fn

        if factory is None:
            return decorator
        return decorator(factory)

    @classmethod
    def create(cls, name: str, *args, **kwargs) -> BaseToolSelector:
        """Create a selector instance by name.
        
        Args:
            name: Registered selector name
            *args, **kwargs: Arguments passed to factory
            
        Returns:
            Selector instance
            
        Raises:
            KeyError: If selector name not registered
        """
        if name not in cls._registry:
            available = ", ".join(cls._registry.keys())
            raise KeyError(
                f"Selector '{name}' not found. Available: {available}. "
                f"Install isage-agentic to get implementations."
            )
        return cls._registry[name](*args, **kwargs)

    @classmethod
    def list_selectors(cls) -> list[str]:
        """List all registered selector names."""
        return list(cls._registry.keys())


# Optional: Generic registry for any plugin type
class PluginRegistry:
    """Generic plugin registry for extensibility."""

    _registries: dict[str, dict[str, Any]] = {}

    @classmethod
    def get_registry(cls, category: str) -> dict[str, Any]:
        """Get or create a registry for a plugin category."""
        if category not in cls._registries:
            cls._registries[category] = {}
        return cls._registries[category]

    @classmethod
    def register(cls, category: str, name: str, factory: Any):
        """Register a plugin in a category."""
        registry = cls.get_registry(category)
        registry[name] = factory

    @classmethod
    def create(cls, category: str, name: str, *args, **kwargs) -> Any:
        """Create a plugin instance."""
        registry = cls.get_registry(category)
        if name not in registry:
            available = ", ".join(registry.keys())
            raise KeyError(
                f"Plugin '{name}' not found in category '{category}'. "
                f"Available: {available}"
            )
        return registry[name](*args, **kwargs)
