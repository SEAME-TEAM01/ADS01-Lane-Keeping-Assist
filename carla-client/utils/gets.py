# ------------------------------------------------------
# Import library
import  os
import  re
import  sys
import  glob
import  pygame
from    utils.prints \
        import  *

# ------------------------------------------------------
# Find carla library
try:
    sys.path.append(config.CARLA_DIR)
    import  carla
except  IndexError:
    print_failure("Failed to import carla egg file.")

# ------------------------------------------------------
def get_weather_presets():
    rgx = re.compile('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)')
    name = lambda x: ' '.join(m.group(0) for m in rgx.finditer(x))
    presets = [x for x in dir(carla.WeatherParameters) if re.match('[A-Z].+', x)]
    return [(getattr(carla.WeatherParameters, x), name(x)) for x in presets]

# ------------------------------------------------------
def get_actor_display_name(actor, truncate=250):
    name = ' '.join(actor.type_id.replace('_', '.').title().split('.')[1:])
    return (name[:truncate - 1] + u'\u2026') if len(name) > truncate else name

# ------------------------------------------------------
def get_actor_blueprints(world, filter, generation):
    bps = world.get_blueprint_library().filter(filter)
    if generation.lower() == "all":
        return bps
    # If the filter returns only one bp, we assume that this one needed and therefore, we ignore the generation
    if len(bps) == 1:
        return bps
    try:
        int_generation = int(generation)
        if int_generation in [1, 2]:
            bps = [x for x in bps if int(x.get_attribute('generation')) == int_generation]
            return bps
        else:
            print_warning("Actor Generation is not valid. No actor will be spawned.")
            print_end()
            return []
    except:
        print_warning("Actor Generation is not valid. No actor will be spawned.")
        print_end()
        return []

# ------------------------------------------------------
def get_font():
    fonts = [x for x in pygame.font.get_fonts()]
    default_font = 'ubuntumono'
    font = default_font if default_font in fonts else fonts[0]
    font = pygame.font.match_font(font)
    return pygame.font.Font(font, 14)

def get_ip(host):
    if host in['localhost', '127.0.0.1']:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.connect(('10.255.255.255', 1))
            host = sock.getsockname()[0]
        except RuntimeError:
            pass
        finally:
            sock.close()
    return host