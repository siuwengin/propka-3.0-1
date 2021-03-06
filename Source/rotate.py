#!/usr/local/bin/python3.0

import math, os, sys, random


def generateCorrespondingAtoms():
    """
    definition of corresponding atoms
    """
    corresponding_atoms = {}
    # initialization
    for resName1 in lib.residueList("standard"):
      corresponding_atoms[resName1] = {}
      for resName2 in lib.residueList("standard"):
        corresponding_atoms[resName1][resName2] = ["N", "CA", "C", "O"]

    corresponding_atoms['ALA']['ALA'].extend(["CA"])


def generalRotationMatrix(axis, theta):
    """
    setting up a rotation matrix for a general rotation around a specified axis.
    """
    cos = math.cos(theta)
    sin = math.sin(theta)
    length = math.sqrt(axis[0]*axis[0] + axis[1]*axis[1] + axis[2]*axis[2])
    Ux = axis[0]/length
    Uy = axis[1]/length
    Uz = axis[2]/length
    R = [[0., 0., 0.], [0., 0., 0.], [0., 0., 0.]]
    #
    # rotation matrix, x-component
    R[0][0] = Ux*Ux + (1-Ux*Ux)*cos
    R[0][1] = Ux*Uy*(1-cos) - Uz*sin
    R[0][2] = Ux*Uz*(1-cos) + Uy*sin
    #
    R[1][0] = Ux*Uy*(1-cos) + Uz*sin
    R[1][1] = Uy*Uy + (1-Uy*Uy)*cos
    R[1][2] = Uy*Uz*(1-cos) - Ux*sin

    R[2][0] = Ux*Uz*(1-cos) - Uy*sin
    R[2][1] = Uy*Uz*(1-cos) + Ux*sin
    R[2][2] = Uz*Uz + (1-Uz*Uz)*cos

    return  R


def generateRotationMatrix(alpha, beta, gamma):
    """
    setting up Euler rotation matrix
    """
    
    # alpha around Z-axis
    cos = math.cos(alpha)
    sin = math.sin(alpha)
    Rz = [[ cos,  sin, 0.00],
          [-sin,  cos, 0.00],
          [0.00, 0.00, 1.00],]
    
    # beta around X-axis
    cos = math.cos(beta)
    sin = math.sin(beta)
    Rx = [[1.00, 0.00, 0.00],
          [0.00,  cos,  sin],
          [0.00, -sin,  cos],]

    R_new = matrixRotation(Rx, Rz)
    
    # gamma around Z-axis
    cos = math.cos(gamma)
    sin = math.sin(gamma)
    Rz = [[ cos,  sin, 0.00],
          [-sin,  cos, 0.00],
          [0.00, 0.00, 1.00],]

    R_new = matrixRotation(Rz, R_new)

    return  R_new
    

def matrixRotation(R, M):
    """
    multiply rotation matrices
    """
    R_new = [[None, None, None],
             [None, None, None],
             [None, None, None],]

    for x in range(3):
      for y in range(3):
        R_new[y][x] = 0.00
        for i in range(3):
          R_new[y][x] += R[y][i] * M[i][x]

    return  R_new
    

def calculateVectorLength(vector):
    """
    calculating the vector length
    """
    return  math.sqrt( vector[0]*vector[0] + vector[1]*vector[1] + vector[2]*vector[2] )
    

def makeScalarProduct(vector1, vector2):
    """
    calculating the scalar product vector1 x vector2
    """
    return  vector1[0]*vector2[0] + vector1[1]*vector2[1] + vector1[2]*vector2[2]
    

def makeCrossProduct(vector1, vector2):
    """
    making cross product vector1 x vector2
    """
    x=0; y=1; z=2
    cross_product = [0.00, 0.00, 0.00]
    cross_product[x] = vector1[y]*vector2[z] - vector1[z]*vector2[y]
    cross_product[y] = vector1[z]*vector2[x] - vector1[x]*vector2[z]
    cross_product[z] = vector1[x]*vector2[y] - vector1[y]*vector2[x]

    return  cross_product
    

def rotateAtom(R, atom):
    """
    multiply rotation matrices
    """

    new_position = [None, None, None]
    #print("atom = ", atom)
    #print("R    = ", R)

    for xyz in range(3):
      new_position[xyz] = 0.00
      for i in range(3):
        new_position[xyz] += R[xyz][i]*atom[i]
        
    return  new_position


def translatePosition(position, translation):
    """
    translates the position according to 'translation'
    """
    for key in position.keys():
      for i in range(3):
        position[key][i] += translation[i]


def rotatePosition(position, axis, theta, center=None):
    """
    rotate the position-dictionary 'theta' around 'axis'
    """
    translate = [0.00, 0.00, 0.00]
    if center == None:
      center = sorted(position.keys())
    for key in center:
      for i in range(3):
        translate[i] += position[key][i]/len(center)

    # translate to rotation center
    for key in position.keys():
      for i in range(3):
        position[key][i] -= translate[i]

    # get rotation matrix
    rotation_matrix = generalRotationMatrix(axis, theta)

    # do the actual rotation
    new_position = [None, None, None]
    for key in position.keys():
      # rotate
      for xyz in range(3):
        new_position[xyz] = translate[xyz]
        for i in range(3):
          new_position[xyz] += rotation_matrix[xyz][i]*position[key][i]
      # update position
      for xyz in range(3):
        position[key][xyz] = new_position[xyz]
      
    return  None


def translateAtoms(atoms, translation):
    """
    rotate an atoms-list 'theta' around 'axis'
    """
    for atom in atoms:
      atom.translate(translation)


def rotateAtoms(atoms, axis, theta, center=None):
    """
    rotate an atoms-list 'theta' around 'axis'
    """
    translate = [0.00, 0.00, 0.00]
    number_of_atoms = 0
    for atom in atoms:
      if atom.name in center or center == None:
        number_of_atoms += 1
        translate[0] += atom.x
        translate[1] += atom.y
        translate[2] += atom.z
    for atom in atoms:
      for i in range(3):
        translate[i] = translate[i]/number_of_atoms

    # translate to rotation center
    for atom in atoms:
      atom.x -= translate[0]
      atom.y -= translate[1]
      atom.z -= translate[2]

    # get rotation matrix
    rotation_matrix = generalRotationMatrix(axis, theta)

    # do the actual rotation
    new_position = [None, None, None]
    for atom in atoms:
      # rotate actual position
      old_position = [atom.x, atom.y, atom.z]
      for xyz in range(3):
        new_position[xyz] = translate[xyz]
        for i in range(3):
          new_position[xyz] += rotation_matrix[xyz][i]*old_position[i]
      # update position
      atom.x = new_position[0]
      atom.y = new_position[1]
      atom.z = new_position[2]

      # rotate configuration
      for key in atom.configurations.keys():
        for xyz in range(3):
          new_position[xyz] = translate[xyz]
          for i in range(3):
            new_position[xyz] += rotation_matrix[xyz][i]*atom.configurations[key][i]
        for xyz in range(3):
          atom.configurations[key][xyz] = new_position[xyz]

    return  None


def generateRandomAxis():
    """
    generates a random axis in 3D space
    """
    alpha = random.uniform(0.00, 2*math.pi)
    beta  = random.uniform(-0.5*math.pi, 0.5*math.pi)

    return  [math.cos(beta)*math.sin(alpha),
             math.cos(beta)*math.cos(alpha),
             math.sin(beta)]


def generateRandomDisplacement(max_dR):
    """
    generates a random distance displacement
    """
    dR    = random.uniform(0.00, max_dR)
    axis  = generateRandomAxis()
    for i in range(3):
      axis[i] = axis[i]*dR

    return  axis


def generateRandomRotation(max_dA):
    """
    generates a random rotation, theta, around a random axis.
    """
    theta = random.uniform(-max_dA, max_dA)

    axis  = generateRandomAxis()

    return  theta, axis


def rotateResidue(R, residue):
    """
    rotate a residue using rotation matrix 'R'
    """

    new_position = [0.00, 0.00, 0.00]
    for atom in residue.atoms:
      for key in atom.configurations:
        for xyz in range(3):
          new_position[xyz] = 0.00
          for i in range(3):
            new_position[xyz] += R[xyz][i]*atom.configurations[key][i]
        for xyz in range(3):
          atom.configurations[key][xyz] = new_position[xyz]
      atom.x = atom.configurations['M0CA'][0]
      atom.y = atom.configurations['M0CA'][1]
      atom.z = atom.configurations['M0CA'][2]
        
    return  None





def main():
    """
    Simple check on rotation
    """

    """"
    --- 1XNB ---
    ATOM    590  N   GLU A  78      26.327  24.519  35.570  1.00  7.60
    ATOM    591  CA  GLU A  78      27.506  24.631  34.705  1.00  7.40
    ATOM    592  C   GLU A  78      26.954  24.323  33.311  1.00  8.10
    ATOM    593  O   GLU A  78      26.373  23.249  33.107  1.00  9.30
    ATOM    594  CB  GLU A  78      28.536  23.577  35.110  1.00  8.00
    ATOM    595  CG  GLU A  78      29.867  23.622  34.344  1.00  9.50
    ATOM    596  CD  GLU A  78      30.828  22.537  34.806  1.00 10.90
    ATOM    597  OE1 GLU A  78      30.382  21.402  35.040  1.00 11.00
    ATOM    598  OE2 GLU A  78      32.047  22.805  34.944  1.00 11.50
    --- 2VUJ ---
    ATOM    669  N   GLU A  89      26.531  24.561  35.581  1.00 11.10            
    ATOM    670  CA  GLU A  89      27.682  24.579  34.689  1.00 11.30            
    ATOM    671  C   GLU A  89      27.147  24.180  33.313  1.00 10.90            
    ATOM    672  O   GLU A  89      26.593  23.066  33.132  1.00 11.20            
    ATOM    673  CB  GLU A  89      28.755  23.595  35.196  1.00 11.00            
    ATOM    674  CG  GLU A  89      30.088  23.632  34.424  1.00 12.60            
    ATOM    675  CD  GLU A  89      31.038  22.566  34.925  1.00 13.00            
    ATOM    676  OE1 GLU A  89      30.526  21.471  35.299  1.00 16.80            
    ATOM    677  OE2 GLU A  89      32.264  22.831  34.980  1.00 12.70            
    """
    import math
    target = []
    target.append(30.828-27.506)
    target.append(22.537-24.631)
    target.append(34.806-34.705)
    str = "   %8.3lf%8.3lf%8.3lf" % (target[0], target[1], target[2])
    #print(str)
    atom = []
    atom.append(31.038-27.682)
    atom.append(22.566-24.579)
    atom.append(34.925-34.689)

    rmsd  = 0.00
    for i in range(3):
      rmsd += pow( (atom[i] - target[i]), 2)
    rmsd = math.sqrt(rmsd)

    str = "%2d %8.3lf%8.3lf%8.3lf%10.3lf" % (0, atom[0], atom[1], atom[2], rmsd)
    print(str)
    axis = [1.0, 1.0, 1.0]

    for iter in range(1, 37):

      if False:
        # print out current
        str = "%2d %8.3lf%8.3lf%8.3lf%10.3lf" % (iter, atom[0], atom[1], atom[2], rmsd)
        print(str)
      
        alpha = random.uniform(-0.10, 0.10)
        beta  = random.uniform(-0.10, 0.10)
        gamma = random.uniform(-0.10, 0.10)

        R_rot = generateRotationMatrix(alpha, beta, gamma)
        #print(R_rot)
        new_position = rotateAtom(R_rot, atom)
      
        new_rmsd = 0.00
        for i in range(3):
          new_rmsd += pow( (new_position[i] - target[i]), 2)
        new_rmsd = math.sqrt(new_rmsd)
      
        if new_rmsd < rmsd:
          rmsd = new_rmsd
          for i in range(3):
            atom[i] = new_position[i]
      else:
        R_rot = generalRotationMatrix(axis, math.pi*iter/18.)
        new_position = rotateAtom(R_rot, atom)
        str = "%2d %8.3lf%8.3lf%8.3lf%10.3lf" % (iter, new_position[0], new_position[1], new_position[2], rmsd)
        print(str)


if __name__ == '__main__': main()

