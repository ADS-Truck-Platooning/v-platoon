import carla

client = carla.Client("localhost", 2000)
world = client.get_world()
spectator = world.get_spectator()

# 긴급 트럭 위치: {100, {0.990f, 30.0f, 2.0f}}
location = carla.Location(x=0.990, y=30.0, z=10.0)
rotation = carla.Rotation(pitch=-30.0, yaw=0.0)

spectator.set_transform(carla.Transform(location, rotation))
