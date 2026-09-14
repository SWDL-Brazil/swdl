"""SWDL Admin package — imports all sub-modules to register routes on admin_bp."""
from routes.admin._helpers import admin_bp  # noqa: F401

# Import all sub-modules so their routes are registered
import routes.admin.dashboard       # noqa: F401
import routes.admin.themes          # noqa: F401
import routes.admin.categories      # noqa: F401
import routes.admin.alerts          # noqa: F401
import routes.admin.news            # noqa: F401
import routes.admin.agenda          # noqa: F401
import routes.admin.inscriptions    # noqa: F401
import routes.admin.delegations     # noqa: F401
import routes.admin.crisis          # noqa: F401
import routes.admin.timer           # noqa: F401
import routes.admin.speakers        # noqa: F401
import routes.admin.dpos            # noqa: F401
import routes.admin.students        # noqa: F401
import routes.admin.convocation     # noqa: F401
import routes.admin.attendance      # noqa: F401
import routes.admin.documents       # noqa: F401
import routes.admin.invocation      # noqa: F401
import routes.admin.certificates    # noqa: F401
import routes.admin.notifications   # noqa: F401
