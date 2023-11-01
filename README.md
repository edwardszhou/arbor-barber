# Arbor Barber  

Blender add-on for generating customizable stochastic fractal trees  

Edward Zhou 05/2023

---

<img width="1471" alt="example" src="https://github.com/edwardszhou/arbor-barber/assets/123663456/22e74a14-5713-4743-8d7f-928b0c0d6378">
  
p5 prototype:  
https://editor.p5js.org/EdwardZ/sketches/6-JZOqOki  

---

**How to use add-on:**  

Blender → Edit → preferences → add-ons → click install → select file → check “Add Mesh: Arbor Barber”  

The tab should appear in the 3D viewport on the right panel!  

---

**Description:**  

Arbor Barber is a Blender add-on that enables users to add customizable stochastic fractal trees into their scene. The add-on provides customization to the trees that allow modification of the size of the tree, its width, the number of branches, the size of its branches, the angle at which the branches split, and the number of levels of branching. It also offers customization to the randomness, allowing users to add variation to the number of branches, size of branches, and angle at which branches split. Additionally, users can apply a wind force to the tree such that it bends in a direction as if it was bowing due to wind. Users can recreate the same tree with different input parameters, or they can randomize the tree with the same input parameters by randomizing the seed. The tree generated consists of one mesh containing the trunk and all the branches, as well as individual meshes for leaves (if the user chooses to enable leaves in the tree generation). These meshes can be further manipulated using Blender by adding materials, modifiers, etc. With this, users can generate large numbers of random trees just be clicking a button. The project also includes the original p5 sketch that the add-on was based on, which contains identical functions with the addition of animation—users can customize wind strength, variation, and chaos to see an animation fractal tree. 
