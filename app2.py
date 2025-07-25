import numpy as np
import streamlit as st
import plotly.express as px

a = 2.46  

def apply_strain(X, Y, strain_percent, strain_angle_deg):
    angle_rad = np.radians(strain_angle_deg)
    strain_fraction = strain_percent / 100.0
    eps_xx = strain_fraction * np.cos(angle_rad) ** 2
    eps_yy = strain_fraction * np.sin(angle_rad) ** 2
    eps_xy = strain_fraction * np.sin(angle_rad) * np.cos(angle_rad)
    strain_matrix = np.array([[1 + eps_xx, eps_xy], [eps_xy, 1 + eps_yy]])
    coords = np.stack([X, Y], axis=-1)
    strained_coords = coords @ strain_matrix.T
    X_strain = strained_coords[..., 0]
    Y_strain = strained_coords[..., 1]
    return X_strain, Y_strain

def graphene_lattice(X, Y, a):
    lattice = np.cos(2 * np.pi * X / a)
    lattice += np.cos(2 * np.pi * (0.5 * X + (np.sqrt(3) / 2 * Y)) / a)
    lattice += np.cos(2 * np.pi * (-0.5 * X + (np.sqrt(3) / 2 * Y)) / a)
    return lattice

def rotate_grid(X, Y, angle_deg):
    angle_rad = np.radians(angle_deg)
    X_rot = X * np.cos(angle_rad) - Y * np.sin(angle_rad)
    Y_rot = X * np.sin(angle_rad) + Y * np.cos(angle_rad)
    return X_rot, Y_rot


st.title("Twisted Graphene Simulator")
st.write("Toggle between bilayer and trilayer graphene, with Quick and High-Res modes.")


system_mode = st.sidebar.radio("Select Graphene System", ("Bilayer", "Trilayer"), key="system_mode")
render_mode = st.sidebar.radio("Select Mode", ("Quick Mode", "High-Res Mode"), key="render_mode")


if render_mode == "Quick Mode":
    st.sidebar.info("Quick Mode: Fast interactive preview")
    extent = st.sidebar.slider("Scan Area Size (Å)", 10, 100, 50, 10, key="extent_quick")
    grid_size = st.sidebar.slider("Resolution (pixels)", 200, 800, 400, 100, key="grid_quick")
else:
    st.sidebar.warning("High-Res Mode: May take time to render!")
    extent = st.sidebar.slider("Scan Area Size (Å)", 50, 500, 200, 50, key="extent_highres")
    grid_size = st.sidebar.slider("Resolution (pixels)", 800, 3000, 1500, 100, key="grid_highres")

x = np.linspace(-extent, extent, grid_size)
y = np.linspace(-extent, extent, grid_size)
X, Y = np.meshgrid(x, y)


st.sidebar.header("Common Parameters")
st.sidebar.subheader("Strain for Layer 1")
strain1 = st.sidebar.slider("Strain (%)", 0.0, 10.0, 2.0, 0.1, key="strain1")
angle1 = st.sidebar.slider("Strain Direction (°)", 0.0, 180.0, 0.0, 1.0, key="angle1")

if system_mode == "Bilayer":
    st.sidebar.header("Bilayer Settings")
    theta_layer2 = st.sidebar.slider("Twist Angle Layer 2 (°)", 0.0, 10.0, 1.1, 0.1, key="theta_layer2")
    st.sidebar.subheader("Strain for Layer 2")
    strain2 = st.sidebar.slider("Strain (%)", 0.0, 10.0, 0.0, 0.1, key="strain2")
    angle2 = st.sidebar.slider("Strain Direction (°)", 0.0, 180.0, 0.0, 1.0, key="angle2")


    X1, Y1 = apply_strain(X, Y, strain1, angle1)
    X2, Y2 = apply_strain(X, Y, strain2, angle2)
    lattice1 = graphene_lattice(X1, Y1, a)
    X2_rot, Y2_rot = rotate_grid(X2, Y2, theta_layer2)
    lattice2 = graphene_lattice(X2_rot, Y2_rot, a)
    combined = lattice1 + lattice2
    title = f"Bilayer Graphene: Twist {theta_layer2}°, Strains {strain1}% / {strain2}%"

else:  
    st.sidebar.header("Trilayer Settings")
    theta_layer2 = st.sidebar.slider("Twist Angle Layer 2 (°)", 0.0, 10.0, 4.8, 0.1, key="theta_layer2_tri")
    theta_layer3 = st.sidebar.slider("Twist Angle Layer 3 (°)", -10.0, 10.0, -1.5, 0.1, key="theta_layer3_tri")
    st.sidebar.subheader("Strain for Layer 2")
    strain2 = st.sidebar.slider("Strain (%)", 0.0, 10.0, 0.0, 0.1, key="strain2_tri")
    angle2 = st.sidebar.slider("Strain Direction (°)", 0.0, 180.0, 0.0, 1.0, key="angle2_tri")
    st.sidebar.subheader("Strain for Layer 3")
    strain3 = st.sidebar.slider("Strain (%)", 0.0, 10.0, 0.0, 0.1, key="strain3_tri")
    angle3 = st.sidebar.slider("Strain Direction (°)", 0.0, 180.0, 0.0, 1.0, key="angle3_tri")

    
    X1, Y1 = apply_strain(X, Y, strain1, angle1)
    X2, Y2 = apply_strain(X, Y, strain2, angle2)
    X3, Y3 = apply_strain(X, Y, strain3, angle3)
    lattice1 = graphene_lattice(X1, Y1, a)
    X2_rot, Y2_rot = rotate_grid(X2, Y2, theta_layer2)
    lattice2 = graphene_lattice(X2_rot, Y2_rot, a)
    X3_rot, Y3_rot = rotate_grid(X3, Y3, theta_layer3)
    lattice3 = graphene_lattice(X3_rot, Y3_rot, a)
    combined = lattice1 + lattice2 + lattice3
    title = f"Trilayer Graphene: Twists {theta_layer2}° / {theta_layer3}°, Strains {strain1}% / {strain2}% / {strain3}%"


fig = px.imshow(
    combined,
    color_continuous_scale='Viridis',
    origin='lower',
    labels={'color': 'Intensity'},
    title=title
)
fig.update_layout(coloraxis_showscale=False)

st.plotly_chart(fig, use_container_width=True)


if render_mode == "High-Res Mode":
    st.download_button(
        label="Download Image",
        data=fig.to_image(format="png"),
        file_name="twisted_graphene.png",
        mime="image/png",
        key="download_button"
    )


st.markdown("---")
st.markdown("<center><small>Creator: Syed Asad Maqbool | Email: syedasad@mail.ustc.edu.cn</small></center>", unsafe_allow_html=True)
