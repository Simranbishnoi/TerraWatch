import axios from 'axios';

// Backend configuration
export const USE_MOCK = false;
export const BASE_URL = 'http://localhost:8000';

// Axios instance
export const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor: attach Authorization header if token exists
api.interceptors.request.use(
  (config) => {
    let token = localStorage.getItem('token');
    if (!token) {
      const savedUser = localStorage.getItem('tw_user');
      if (savedUser) {
        try {
          const parsed = JSON.parse(savedUser);
          token = parsed.token;
        } catch (e) {
          // Ignore JSON parse error
        }
      }
    }

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor: global 401 error handler (auto logout & redirect)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Clear user credentials
      localStorage.removeItem('token');
      localStorage.removeItem('tw_user');

      // Redirect to /login if not already on login or signup pages
      if (
        typeof window !== 'undefined' &&
        !window.location.pathname.includes('/login') &&
        !window.location.pathname.includes('/signup')
      ) {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export async function login(email, password) {
  if (USE_MOCK) {
    await new Promise((resolve) => setTimeout(resolve, 600));
    if (!email || !password) {
      throw new Error('Please provide email and password');
    }
    return {
      token: 'mock-jwt-token-terrawatch',
      email: email,
      name: email.split('@')[0],
    };
  }

  try {
    const response = await api.post('/login', { email, password });
    const data = response.data;
    return {
      token: data.access_token,
      access_token: data.access_token,
      token_type: data.token_type,
      mfa_required: data.mfa_required,
      email: email,
      name: email.split('@')[0],
    };
  } catch (err) {
    const detail =
      err.response?.data?.detail || err.message || 'Invalid email or password';
    throw new Error(detail);
  }
}

export async function signup(email, password, name) {
  if (USE_MOCK) {
    await new Promise((resolve) => setTimeout(resolve, 600));
    if (!email || !password) {
      throw new Error('Please fill in all required fields');
    }
    return {
      token: 'mock-jwt-token-terrawatch',
      email: email,
      name: name || 'Demo User',
    };
  }

  try {
    // Send email and password to /signup endpoint
    const response = await api.post('/signup', { email, password });
    const userData = response.data;

    // Automatically log in to get access token for smooth user onboarding
    let token = null;
    try {
      const loginRes = await api.post('/login', { email, password });
      token = loginRes.data?.access_token;
    } catch (e) {
      // Login fallback if auto-login fails
    }

    return {
      id: userData.id,
      email: userData.email,
      token: token,
      name: name || email.split('@')[0],
    };
  } catch (err) {
    const detail =
      err.response?.data?.detail || err.message || 'Failed to create account';
    throw new Error(detail);
  }
}

// -------------------------------------------------------------
// Mock Data & Simulation Endpoints for TerraWatch Features
// -------------------------------------------------------------

const MOCK_FARMS = [
  {
    id: 'farm-1',
    name: 'Fazenda Santa Maria',
    status: 'HIGH',
    loss: '12.4 ha lost',
    lat: -10.5124,
    lng: -62.2158,
    areaHa: 12.4,
  },
  {
    id: 'farm-2',
    name: 'Rancho Verde Norte',
    status: 'HIGH',
    loss: '18.7 ha lost',
    lat: -10.4289,
    lng: -62.1542,
    areaHa: 18.7,
  },
  {
    id: 'farm-3',
    name: 'Agroflorestal Nova Vida',
    status: 'MEDIUM',
    loss: '5.2 ha lost',
    lat: -10.6311,
    lng: -62.3105,
    areaHa: 5.2,
  },
  {
    id: 'farm-4',
    name: 'Fazenda Rio Bonito',
    status: 'OK',
    loss: '0.0 ha lost',
    lat: -10.3841,
    lng: -62.0917,
    areaHa: 0.0,
  },
  {
    id: 'farm-5',
    name: 'Estância Esperança',
    status: 'OK',
    loss: '0.4 ha lost',
    lat: -10.5982,
    lng: -62.1894,
    areaHa: 0.4,
  },
];

export async function getFarms() {
  try {
    const response = await api.get('/api/farms');
    return response.data;
  } catch (err) {
    console.error("Failed to fetch farms:", err);
    return MOCK_FARMS; // Fallback to mock if it fails
  }
}

export async function addFarm(farmData) {
  try {
    const payload = {
      name: farmData.name,
      latitude: parseFloat(farmData.latitude || farmData.lat || 0),
      longitude: parseFloat(farmData.longitude || farmData.lng || 0),
      status: (farmData.status || 'OK').toUpperCase(),
      hectares_lost: parseFloat(farmData.hectares_lost || farmData.loss || 0),
    };

    const response = await api.post('/api/farms', payload);
    return response.data;
  } catch (err) {
    console.error("Failed to add farm via API:", err);
    // Fallback simulated farm object
    const fallbackFarm = {
      id: Date.now(),
      name: farmData.name,
      latitude: parseFloat(farmData.latitude || 0),
      longitude: parseFloat(farmData.longitude || 0),
      status: (farmData.status || 'OK').toUpperCase(),
      hectares_lost: parseFloat(farmData.hectares_lost || 0),
      loss: `${parseFloat(farmData.hectares_lost || 0)} ha lost`,
      lat: parseFloat(farmData.latitude || 0),
      lng: parseFloat(farmData.longitude || 0),
      areaHa: parseFloat(farmData.hectares_lost || 0),
    };
    MOCK_FARMS.unshift(fallbackFarm);
    return fallbackFarm;
  }
}


export async function analyze(polygon, dateStart, dateEnd) {
  try {
    const payload = {
      farm_id: 1,
      boundary: {
        type: "Polygon",
        coordinates: [polygon || []]
      },
      start_date: dateStart || "2023-01-01",
      end_date: dateEnd || "2024-01-01",
      previous_observation_date: "2023-06-01"
    };
    
    // Call our new backend endpoint!
    const response = await api.post('/api/analysis/analyze', payload);
    const data = response.data;
    
    return {
      risk: data.risk_level || 'HIGH',
      score: data.risk_score ? data.risk_score * 100 : 87,
      hectaresLost: `${data.forest_loss_hectares || 12.4} ha`,
      manipulationScore: data.boundary_manipulation_score || '0.87',
      dateStart: dateStart || '2023-01-01',
      dateEnd: dateEnd || '2024-01-01',
      evidence: data.evidence_summary || [
        'Analysis completed by TerraWatch Satellite Engine.'
      ],
      lossGeoJson: data.loss_geojson
    };
  } catch (err) {
    console.error("Analysis failed:", err);
    throw new Error(err.response?.data?.detail || err.message || 'Analysis failed');
  }
}

const MOCK_REPORTS = [
  {
    id: 'REP-2024-0891',
    farm_name: 'Fazenda Santa Maria',
    farmName: 'Fazenda Santa Maria',
    status: 'HIGH',
    date: 'Oct 14, 2024',
    fileSize: '2.4 MB',
  },
  {
    id: 'REP-2024-0842',
    farm_name: 'Rancho Verde Norte',
    farmName: 'Rancho Verde Norte',
    status: 'HIGH',
    date: 'Oct 12, 2024',
    fileSize: '3.1 MB',
  },
  {
    id: 'REP-2024-0815',
    farm_name: 'Fazenda Esperança',
    farmName: 'Fazenda Esperança',
    status: 'MEDIUM',
    date: 'Oct 08, 2024',
    fileSize: '2.7 MB',
  },
  {
    id: 'REP-2024-0799',
    farm_name: 'Fazenda Rio Bonito',
    farmName: 'Fazenda Rio Bonito',
    status: 'OK',
    date: 'Sep 28, 2024',
    fileSize: '1.8 MB',
  },
  {
    id: 'REP-2024-0774',
    farm_name: 'Rancho Fundo',
    farmName: 'Rancho Fundo',
    status: 'HIGH',
    date: 'Sep 22, 2024',
    fileSize: '4.2 MB',
  },
  {
    id: 'REP-2024-0752',
    farm_name: 'Sítio Boa Vista',
    farmName: 'Sítio Boa Vista',
    status: 'OK',
    date: 'Sep 17, 2024',
    fileSize: '1.9 MB',
  },
  {
    id: 'REP-2024-0731',
    farm_name: 'Agroflorestal Nova Vida',
    farmName: 'Agroflorestal Nova Vida',
    status: 'MEDIUM',
    date: 'Sep 11, 2024',
    fileSize: '2.6 MB',
  },
  {
    id: 'REP-2024-0710',
    farm_name: 'Estância Esperança',
    farmName: 'Estância Esperança',
    status: 'OK',
    date: 'Sep 05, 2024',
    fileSize: '2.1 MB',
  },
  {
    id: 'REP-2024-0688',
    farm_name: 'Fazenda Bela Alvorada',
    farmName: 'Fazenda Bela Alvorada',
    status: 'HIGH',
    date: 'Aug 29, 2024',
    fileSize: '3.8 MB',
  },
  {
    id: 'REP-2024-0665',
    farm_name: 'Vale do Guaporé Agrícola',
    farmName: 'Vale do Guaporé Agrícola',
    status: 'MEDIUM',
    date: 'Aug 21, 2024',
    fileSize: '2.5 MB',
  },
  {
    id: 'REP-2024-0640',
    farm_name: 'Fazenda Primavera do Sul',
    farmName: 'Fazenda Primavera do Sul',
    status: 'OK',
    date: 'Aug 15, 2024',
    fileSize: '1.7 MB',
  },
  {
    id: 'REP-2024-0618',
    farm_name: 'Recanto dos Ipês',
    farmName: 'Recanto dos Ipês',
    status: 'MEDIUM',
    date: 'Aug 08, 2024',
    fileSize: '2.9 MB',
  },
  {
    id: 'REP-2024-0592',
    farm_name: 'Cooperativa Agro Verde',
    farmName: 'Cooperativa Agro Verde',
    status: 'OK',
    date: 'Jul 30, 2024',
    fileSize: '2.2 MB',
  },
];

export async function getReports() {
  try {
    const response = await api.get('/api/reports');
    return response.data;
  } catch (err) {
    console.error("Failed to fetch reports:", err);
    return MOCK_REPORTS; // Fallback to mock if it fails
  }
}

export async function downloadReport(reportId) {
  await new Promise((resolve) => setTimeout(resolve, 400));
  return { success: true, reportId };
}
