'use client';

import { useRef, useMemo, useState, useEffect } from 'react';
import { Canvas, useFrame, useLoader } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import * as THREE from 'three';

/* ── GLSL shaders (from WebGL Globe / dataarts) ─── */
const earthVertexShader = `
  varying vec3 vNormal;
  varying vec2 vUv;
  void main() {
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    vNormal = normalize(normalMatrix * normal);
    vUv = uv;
  }
`;

const earthFragmentShader = `
  uniform sampler2D uTexture;
  varying vec3 vNormal;
  varying vec2 vUv;
  void main() {
    vec3 diffuse = texture2D(uTexture, vUv).xyz;
    float intensity = 1.05 - dot(vNormal, vec3(0.0, 0.0, 1.0));
    vec3 atmosphere = vec3(1.0, 1.0, 1.0) * pow(intensity, 3.0);
    gl_FragColor = vec4(diffuse + atmosphere, 1.0);
  }
`;

const atmosphereVertexShader = `
  varying vec3 vNormal;
  void main() {
    vNormal = normalize(normalMatrix * normal);
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
  }
`;

const atmosphereFragmentShader = `
  varying vec3 vNormal;
  void main() {
    float intensity = pow(0.7 - dot(vNormal, vec3(0, 0, 1.0)), 8.0);
    gl_FragColor = vec4(0.4, 0.6, 1.0, 1.0) * intensity * 0.6;
  }
`;

/* ── Lat/Lng → 3D ─── */
function latLngToVector3(lat: number, lng: number, radius: number): THREE.Vector3 {
  const phi = (90 - lat) * (Math.PI / 180);
  const theta = (lng + 180) * (Math.PI / 180);
  return new THREE.Vector3(
    -radius * Math.sin(phi) * Math.cos(theta),
    radius * Math.cos(phi),
    radius * Math.sin(phi) * Math.sin(theta),
  );
}

/* ── Earth sphere with real world.jpg texture + GLSL ─── */
function Earth() {
  const meshRef = useRef<THREE.Mesh>(null);
  const texture = useLoader(THREE.TextureLoader, '/img/world.jpg');

  const uniforms = useMemo(() => ({
    uTexture: { value: texture },
  }), [texture]);

  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.y += 0.0015;
      meshRef.current.rotation.x = Math.sin(state.clock.elapsedTime * 0.25) * 0.04;
    }
  });

  return (
    <mesh ref={meshRef}>
      <sphereGeometry args={[2, 64, 64]} />
      <shaderMaterial
        vertexShader={earthVertexShader}
        fragmentShader={earthFragmentShader}
        uniforms={uniforms}
      />
    </mesh>
  );
}

/* ── Atmosphere glow (from WebGL Globe) ─── */
function Atmosphere() {
  const meshRef = useRef<THREE.Mesh>(null);

  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.y += 0.0015;
    }
  });

  return (
    <mesh ref={meshRef} scale={[1.12, 1.12, 1.12]}>
      <sphereGeometry args={[2, 64, 64]} />
      <shaderMaterial
        vertexShader={atmosphereVertexShader}
        fragmentShader={atmosphereFragmentShader}
        side={THREE.BackSide}
        blending={THREE.AdditiveBlending}
        transparent
      />
    </mesh>
  );
}

/* ── Gold decorative rings ─── */
function GoldRings() {
  const groupRef = useRef<THREE.Group>(null);

  useFrame((state) => {
    if (groupRef.current) {
      groupRef.current.rotation.y += 0.001;
      groupRef.current.rotation.z = Math.sin(state.clock.elapsedTime * 0.2) * 0.1;
    }
  });

  return (
    <group ref={groupRef}>
      <mesh rotation={[Math.PI / 2, 0, 0]}>
        <torusGeometry args={[2.3, 0.006, 8, 128]} />
        <meshStandardMaterial color="#C9A84C" transparent opacity={0.35} />
      </mesh>
      <mesh rotation={[Math.PI / 3, Math.PI / 4, 0]}>
        <torusGeometry args={[2.5, 0.004, 8, 128]} />
        <meshStandardMaterial color="#C9A84C" transparent opacity={0.18} />
      </mesh>
    </group>
  );
}

/* ── Floating particles ─── */
function Particles() {
  const ref = useRef<THREE.Points>(null);

  useFrame((state) => {
    if (ref.current) {
      ref.current.rotation.y += 0.0004;
      ref.current.rotation.x = Math.sin(state.clock.elapsedTime * 0.12) * 0.04;
    }
  });

  const positions = useMemo(() => {
    const arr = new Float32Array(120 * 3);
    for (let i = 0; i < 120; i++) {
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      const r = 3 + Math.random() * 2;
      arr[i * 3] = r * Math.sin(phi) * Math.cos(theta);
      arr[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
      arr[i * 3 + 2] = r * Math.cos(phi);
    }
    return arr;
  }, []);

  return (
    <points ref={ref}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" count={120} array={positions} itemSize={3} />
      </bufferGeometry>
      <pointsMaterial size={0.012} color="#C9A84C" transparent opacity={0.45} sizeAttenuation />
    </points>
  );
}

/* ── Data points (lat/lng bars like WebGL Globe) ─── */
const DATA_POINTS: [number, number, number][] = [
  [-23.55, -46.63, 1.0],   // São Paulo
  [-22.91, -43.17, 0.8],   // Rio de Janeiro
  [-15.78, -47.93, 0.6],   // Brasília
  [40.71, -74.01, 0.5],    // New York
  [51.51, -0.13, 0.4],     // London
  [48.86, 2.35, 0.4],      // Paris
  [52.52, 13.41, 0.3],     // Berlin
  [55.76, 37.62, 0.3],     // Moscow
  [35.68, 139.69, 0.5],    // Tokyo
  [39.90, 116.40, 0.5],    // Beijing
  [28.61, 77.21, 0.4],     // New Delhi
  [25.20, 55.27, 0.3],     // Dubai
  [-33.87, 151.21, 0.3],   // Sydney
  [1.35, 103.82, 0.3],     // Singapore
  [19.43, -99.13, 0.4],    // Mexico City
  [-34.60, -58.38, 0.4],   // Buenos Aires
  [-22.91, -43.20, 0.9],   // Rio (extra glow)
  [41.01, 28.98, 0.3],     // Istanbul
  [-1.29, 36.82, 0.3],     // Nairobi
  [30.04, 31.24, 0.3],     // Cairo
  [37.57, 126.98, 0.4],    // Seoul
  [13.76, 100.50, 0.3],    // Bangkok
];

function DataPoints() {
  const groupRef = useRef<THREE.Group>(null);
  const meshRef = useRef<THREE.InstancedMesh>(null);

  useFrame((state) => {
    if (groupRef.current) {
      groupRef.current.rotation.y += 0.0015;
      groupRef.current.rotation.x = Math.sin(state.clock.elapsedTime * 0.25) * 0.04;
    }
  });

  const dummy = useMemo(() => new THREE.Object3D(), []);
  const barGeo = useMemo(() => new THREE.BoxGeometry(0.015, 0.015, 1), []);

  useEffect(() => {
    if (!meshRef.current) return;
    DATA_POINTS.forEach(([lat, lng, mag], i) => {
      const pos = latLngToVector3(lat, lng, 2.02);
      const normal = pos.clone().normalize();
      dummy.position.copy(pos);
      dummy.lookAt(pos.clone().add(normal));
      dummy.scale.set(1, 1, mag * 0.4);
      dummy.updateMatrix();
      meshRef.current!.setMatrixAt(i, dummy.matrix);
    });
    meshRef.current.instanceMatrix.needsUpdate = true;
  }, [dummy]);

  return (
    <group ref={groupRef}>
      <instancedMesh ref={meshRef} args={[barGeo, undefined, DATA_POINTS.length]}>
        <meshBasicMaterial color="#C9A84C" transparent opacity={0.8} />
      </instancedMesh>
    </group>
  );
}

/* ── Loading fallback ─── */
function GlobeLoader() {
  return (
    <div className="w-full h-full min-h-[400px] flex items-center justify-center">
      <div className="w-8 h-8 border-2 border-gold border-t-transparent rounded-full animate-spin" />
    </div>
  );
}

/* ── Main export ─── */
export function Globe3D() {
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const img = new Image();
    img.src = '/img/world.jpg';
    img.onload = () => setReady(true);
  }, []);

  if (!ready) return <GlobeLoader />;

  return (
    <div className="w-full h-full min-h-[400px]">
      <Canvas camera={{ position: [0, 0, 5.5], fov: 45 }} style={{ background: 'transparent' }}>
        <ambientLight intensity={0.3} />
        <pointLight position={[10, 10, 10]} intensity={1.0} />
        <pointLight position={[-10, -5, -10]} intensity={0.3} color="#C9A84C" />

        <Earth />
        <Atmosphere />
        <DataPoints />
        <GoldRings />
        <Particles />

        <OrbitControls
          enableZoom={false}
          enablePan={false}
          autoRotate
          autoRotateSpeed={0.3}
          maxPolarAngle={Math.PI / 1.3}
          minPolarAngle={Math.PI / 3}
        />
      </Canvas>
    </div>
  );
}
