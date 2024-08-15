def set_voltage_gate(gate_name, value):
    print(f"Setting {gate_name} to {value}")
    # Use getattr to dynamically get the gate attribute from the gates module
    getattr(gates, gate_name)(value)  # Uncomment this line when using actual hardware


def measure_current():
    currents = station.components['currents']
    try:
        # Assuming 'currents' is a properly initialized and configured QCoDeS instrument
        time.sleep(0.2)  # Wait for 0.2 seconds before taking the measurement
        return float(currents.O1current())  # Make sure O1current is the correct attribute
    except pyvisa.errors.VisaIOError as e:
        print(f"Error measuring current: {e}")
        return None  # Return None or a default value if an error occurs    

def measure_current_across_grid(barrierx,barriery,angle, V_low_B3, V_high_B3, V_low_B4, V_high_B4,resolution):
    """
    Measures current along a specific angle across the entire B3-B4 voltage grid.
    """
    # Define the direction vector based on the angle
    start_point = np.array([0, 0])
    direction = np.array([np.cos(angle), np.sin(angle)])
    # Avoid division by very small values to prevent overflow
    if np.abs(direction[0]) < 1e-10:
        direction[0] = 1e-10
    if np.abs(direction[1]) < 1e-10:
        direction[1] = 1e-10
    # Calculate end_point where the line intersects with the voltage boundaries
    x_intersect = V_low_B3 if direction[0] < 0 else V_high_B3
    y_intersect = V_low_B4 if direction[1] < 0 else V_high_B4
    t_x = (x_intersect) / direction[0]
    t_y = (y_intersect) / direction[1]
    # Select the intersection that occurs first
    if t_x > 0 and (t_x < t_y or t_y <= 0):
        end_point = np.array([x_intersect, t_x * direction[1]])
        print(f"end_point is {end_point}")
    elif t_y > 0:
        end_point = np.array([t_y * direction[0], y_intersect])
        print(f"end_point is {end_point}")
    else:
        raise ValueError(f"No valid intersection for angle {np.degrees(angle)}°")
    
    # Create line points
    t_values = np.linspace(0, 1, resolution)
    line_points = np.linspace(start_point, end_point, resolution)

    # Measure current at each point along the line
    currents = []
    for point in line_points:
        set_voltage_gate(barrierx, point[0])
        set_voltage_gate(barriery, point[1])
        current = np.abs(measure_current())
        currents.append(current)
 
    angle_deg = np.degrees(angle)  # Convert radians to degrees
    return np.column_stack((line_points, currents, [angle_deg] * len(currents)))