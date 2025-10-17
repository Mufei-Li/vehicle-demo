import React, { useState, useEffect, useRef } from "react";
import {
  Layout,
  Menu,
  Button,
  Modal,
  Form,
  Input,
  Tabs,
  Card,
  Switch,
  Upload,
  List,
  Avatar,
  Tag,
  Collapse,
  message,
  Alert,
} 
from "antd";
import {
  PlusOutlined,
  UploadOutlined,
  FolderOutlined,
  FileImageOutlined,
  CaretRightOutlined,
  SearchOutlined,
  AimOutlined,
} 
from "@ant-design/icons";
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import exifr from "exifr";
import AMapLoader from "@amap/amap-jsapi-loader";
import { message as AntMessage } from "antd";

const { Header, Content, Sider } = Layout;
const { Panel } = Collapse;

const COLORS = ["#0088FE", "#00C49F", "#FFBB28", "#FF8042"];

const API_BASE_URL = "https://ragpp-vehicle-detection-backend.hf.space";

function App() {
  const [showRegister, setShowRegister] = useState(false);
  const [loggedIn, setLoggedIn] = useState(false);
  const [projects, setProjects] = useState([]);
  const [isRestored, setIsRestored] = useState(false);


// 页面加载时，从 localStorage 恢复保存的项目数据（并修复 createdAt）
useEffect(() => {
  try {
    const saved = localStorage.getItem("projects");
    if (!saved) return;

    const parsed = JSON.parse(saved);
    // 将 createdAt (ISO string) 转回 Date 对象
    const restored = parsed.map((p) => ({
      ...p,
      videoTasks: (p.videoTasks || []).map((t) => ({
        ...t,
        // 如果是 ISO 字符串则转 Date，否则保留
        createdAt: t.createdAt ? new Date(t.createdAt) : null,
        // file 仍然为 null（文件需要用户重新上传）
        file: null,
      })),
    }));

    setProjects(restored);

    // 可选：如果之前没有 currentProject，自动选第一个
    if (restored.length > 0) {
      setCurrentProject(restored[0]);
    }
  } catch (err) {
    console.error("从 localStorage 恢复 projects 失败:", err);
    localStorage.removeItem("projects");
  }
}, []);

// 每当 projects 更新时，将其保存到 localStorage
useEffect(() => {
if (!isRestored) return; // ✅ 未恢复完成前不保存
console.log("💾 正在保存 projects:", projects);  
  try {
    const serializable = projects.map((p) => ({
      id: p.id,
      name: p.name,
      // videoTasks 保留可序列化的字段（不保存 file 对象）
      videoTasks: (p.videoTasks || []).map((t) => ({
        id: t.id,
        name: t.name,
        // createdAt 统一保存为 ISO 字符串
        createdAt: t.createdAt ? (t.createdAt instanceof Date ? t.createdAt.toISOString() : t.createdAt) : null,
        location: t.location || null,
        shareAllowed: !!t.shareAllowed,
        // analysisResults 里应该全部是可序列化字段（数字/数组/对象）
        analysisResults: t.analysisResults || null,
      })),
    }));
    localStorage.setItem("projects", JSON.stringify(serializable));
  } catch (err) {
    console.error("保存 projects 到 localStorage 失败:", err);
  }
}, [projects]);



  const [currentProject, setCurrentProject] = useState(null);
  const [currentVideoTask, setCurrentVideoTask] = useState(null);
  const [isProjectModalVisible, setIsProjectModalVisible] = useState(false);
  const [uploadList, setUploadList] = useState([]);
  const [analysisActiveKey, setAnalysisActiveKey] = useState([]);
  const [processedFiles, setProcessedFiles] = useState(new Set());
  const [previewUrl, setPreviewUrl] = useState(null);
  const [searchValue, setSearchValue] = useState("");
  const [analysisParams, setAnalysisParams] = useState({
    plateNumber: true,
    vehicleBrand: true,
    vehicleType: true,
    plateColor: false,
    vehicleModel: false,
    vehicleColor: false,
    newEnergy: false,
  });
  const [analyzing, setAnalyzing] = useState(false);
  const [messageApi, contextHolder] = AntMessage.useMessage();

  const mapRef = useRef(null);
  const markerRef = useRef(null);

  const handleLogin = async (values, loginType) => {
  try {
    let formData = new FormData();
    
    if (loginType === 'email') {
      formData.append('identifier', values.email);
      formData.append('password', values.password);
    } else if (loginType === 'phone') {
      formData.append('identifier', values.phone);
      formData.append('password', values.password);
    }

    const response = await fetch(`${API_BASE_URL}/login`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || '登录失败');
    }

    const result = await response.json();
    
    // 保存 token 到 localStorage
    localStorage.setItem('access_token', result.access_token);
    setLoggedIn(true);
    message.success('登录成功！');
    
  } catch (error) {
    console.error('登录错误:', error);
    message.error(error.message);
  }
};


  const showCreateProject = () => setIsProjectModalVisible(true);
  const handleRegister = async (values) => {
  try {
    const formData = new FormData();
    if (values.email) formData.append("email", values.email);
    if (values.phone) formData.append("phone", values.phone);
    formData.append("password", values.password);

    const res = await fetch(`${API_BASE_URL}/register`, {
      method: "POST",
      body: formData,
    });

    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.detail || "注册失败");
    }

    message.success(data.message || "注册成功，请登录。");
    setShowRegister(false);
  } catch (err) {
    console.error("注册错误:", err);
    message.error(err.message);
  }
};


// 处理邮箱/手机号+密码登录
const handleEmailLogin = async (values) => {
  try {
    const formData = new FormData();
    formData.append("identifier", values.identifier);
    formData.append("password", values.password);

    const res = await fetch(`${API_BASE_URL}/login`, {
      method: "POST",
      body: formData,
    });

    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.detail || "登录失败");
    }

    messageApi.success("登录成功！");
    localStorage.setItem("access_token", data.access_token);
    setLoggedIn(true);
  } catch (err) {
    console.error("登录错误:", err);
    messageApi.error(err.message);
  }
};

const handleLogout = () => {
  // 清除登录凭证
  localStorage.removeItem("access_token");
  localStorage.removeItem("user_id");

  // 清除所有项目数据（包括视频与分析结果）
  localStorage.removeItem("projects");

  // 清除当前会话状态
  setLoggedIn(false);
  setCurrentProject(null);
  setCurrentVideoTask(null);
  setProjects([]); // 同步清空内存中数据
   
   projects.forEach((p) => {
  p.videoTasks.forEach((t) => {
    deleteVideoFromDB(`${p.id}_${t.id}`);
  });
});

  messageApi.success("已退出登录");
};

  const handleCreateProject = (values) => {
  const newProject = { name: values.name, id: Date.now(), videoTasks: [] };
  setProjects((prev) => {
    const next = [...prev, newProject];
    return next;
  });
  setCurrentProject(newProject);
  setIsProjectModalVisible(false);
};


  const handleUploadChange = ({ fileList }) => {
  setUploadList(fileList);

  // 找出本次新增的文件（用 uid 去重）
  const newFiles = fileList.filter((file) => !processedFiles.has(file.uid));

  if (newFiles.length > 0 && currentProject) {
    const newProcessedFiles = new Set(processedFiles);
    newFiles.forEach((file) => newProcessedFiles.add(file.uid));

    // 构造 videoTasks（包含 file 对象供当前会话使用）
    const newVideoTasks = newFiles.map((file) => ({
      id: file.uid,
      name: file.name,
      file: file.originFileObj || file,
      preview: file.originFileObj ? URL.createObjectURL(file.originFileObj) : undefined,
      location: null,
      shareAllowed: false,
      analysisResults: null,
      createdAt: new Date(),
    }));

    // 更新 projects（函数式更新更安全）
    setProjects((prevProjects) => {
      const updated = prevProjects.map((project) => {
        if (project.id === currentProject.id) {
          return { ...project, videoTasks: [...(project.videoTasks || []), ...newVideoTasks] };
        }
        return project;
      });
      return updated;
    });

    // 更新 currentProject 引用为最新对象
    setCurrentProject((prev) => {
      if (!prev) return prev;
      return {
        ...prev,
        videoTasks: [...(prev.videoTasks || []), ...newVideoTasks],
      };
    });

    setProcessedFiles(newProcessedFiles);
    messageApi.success(`成功添加 ${newFiles.length} 个文件`);

    // 保存每个文件到 IndexedDB（异步，但不阻塞 UI）
    newFiles.forEach((file) => {
      const id = `${currentProject.id}_${file.uid}`;
      const blob = file.originFileObj || file; // File/Blob
      saveVideoToDB(id, blob)
        .then(() => {
          console.log("Saved video to DB:", id);
        })
        .catch((err) => {
          console.error("保存视频到 DB 失败:", id, err);
        });
    });
  }
};


  const getCurrentProjectVideoTasks = () =>
    currentProject ? currentProject.videoTasks : [];
  
  // 页面加载时，从 localStorage 恢复登录状态 + 保存的项目
useEffect(() => {
  const token = localStorage.getItem("access_token");
  if (token) {
    setLoggedIn(true);
  }

  try {
    const saved = localStorage.getItem("projects");
    if (!saved) return;

    const parsed = JSON.parse(saved);
    const restored = parsed.map((p) => ({
      ...p,
      videoTasks: (p.videoTasks || []).map((t) => ({
        ...t,
        createdAt: t.createdAt ? new Date(t.createdAt) : null,
        file: null,
      })),
    }));

    setProjects(restored);

    if (restored.length > 0) {
      setCurrentProject(restored[0]);
    }
  } catch (err) {
    console.error("从 localStorage 恢复 projects 失败:", err);
    localStorage.removeItem("projects");
  } finally {
    setIsRestored(true); // ✅ 一定要加上 finally
  }
}, []);

useEffect(() => {
  if (!isRestored || projects.length === 0) return;

  // 遍历每个项目和任务
  projects.forEach((project) => {
    project.videoTasks.forEach(async (task) => {
      const id = `${project.id}_${task.id}`;
      const file = await getVideoFromDB(id);
      if (file) {
        // 生成临时URL，用于预览
        task.file = file;
        task.preview = URL.createObjectURL(file);
        // 触发状态更新
        setProjects((prev) =>
          prev.map((p) =>
            p.id === project.id
              ? {
                  ...p,
                  videoTasks: p.videoTasks.map((t) =>
                    t.id === task.id ? { ...task } : t
                  ),
                }
              : p
          )
        );
      }
    });
  });
}, [isRestored]);



  useEffect(() => {
    if (!currentVideoTask?.file) return;
    const url = URL.createObjectURL(currentVideoTask.file);
    setPreviewUrl(url);
    return () => {
      URL.revokeObjectURL(url);
      setPreviewUrl(null);
    };
  }, [currentVideoTask?.file]);

  useEffect(() => {
    async function readVideoGPS() {
      if (currentVideoTask?.file && !currentVideoTask.location) {
        try {
          const gps = await exifr.gps(currentVideoTask.file);
          if (gps && gps.latitude && gps.longitude) {
            updateTaskLocation({ lat: gps.latitude, lng: gps.longitude });
            message.success("已从视频读取地理位置信息");
          }
        } catch (err) {
          console.warn("未能读取视频 EXIF", err);
        }
      }
    }
    readVideoGPS();
  }, [currentVideoTask?.file]);

  // 初始化地图
useEffect(() => {
  if (!currentVideoTask) return;

  AMapLoader.load({
    key: "48ccf7eb8007514617c7977323a00f5f",
    version: "2.0",
    plugins: ["AMap.Marker", "AMap.ToolBar", "AMap.PlaceSearch"],
  }).then((AMap) => {
    // 如果已有地图实例，先销毁旧的
    if (mapRef.current) {
      try {
    	mapRef.current.destroy();
      } catch (e) {
    	console.warn("地图销毁异常", e);
      }
      mapRef.current = null;
    }

    const center = currentVideoTask.location
      ? [currentVideoTask.location.lng, currentVideoTask.location.lat]
      : [116.397428, 39.90923];

    // 初始化新地图
    mapRef.current = new AMap.Map("amap-container", {
      viewMode: "2D",
      zoom: 12,
      center,
    });

    // 添加标记
    markerRef.current = new AMap.Marker({
      position: center,
      map: mapRef.current,
    });

    // 点击地图更新位置
    mapRef.current.on("click", (e) => {
      const latlng = { lat: e.lnglat.getLat(), lng: e.lnglat.getLng() };
      updateTaskLocation(latlng);
      message.success("已手动标注位置");
    });
  }).catch((err) => console.error("地图加载失败:", err));
}, [currentVideoTask]); // 每次切换视频任务重新加载地图

// 更新任务地理位置
const updateTaskLocation = (latlng) => {
  const updatedProjects = projects.map((project) => {
    if (project.id === currentProject.id) {
      const updatedTasks = project.videoTasks.map((task) => {
        if (task.id === currentVideoTask.id) return { ...task, location: latlng };
        return task;
      });
      return { ...project, videoTasks: updatedTasks };
    }
    return project;
  });
  setProjects(updatedProjects);
  setCurrentVideoTask({ ...currentVideoTask, location: latlng });

  if (mapRef.current) {
    // 记住当前缩放级别
    const currentZoom = mapRef.current.getZoom();

    // 若已有标记则移动，否则新建
    if (markerRef.current) {
      markerRef.current.setPosition([latlng.lng, latlng.lat]);
    } else {
      markerRef.current = new window.AMap.Marker({
        position: [latlng.lng, latlng.lat],
        map: mapRef.current,
      });
    }

    // 临时禁用事件监听，防止重复触发
    const map = mapRef.current;
    const handleMoveEnd = () => {
      map.setZoom(currentZoom);
      map.off("moveend", handleMoveEnd); // 一次性事件
    };

    // 移动中心，并在移动完成后恢复缩放
    map.on("moveend", handleMoveEnd);
    map.setCenter([latlng.lng, latlng.lat]);
  }
};

  // 搜索地点
const handleSearchPlace = () => {
  console.log("🔍 handleSearchPlace triggered, value =", searchValue);
  if (!searchValue || !mapRef.current) {
    message.warning("请输入要搜索的地点名称");
    return;
  }
  if (!searchValue || !mapRef.current) {
    message.warning("请输入要搜索的地点名称");
    return;
  }

  AMapLoader.load({
    key: "46046dbf9deeb823d973ca202a961710",
    version: "2.0",
    plugins: ["AMap.PlaceSearch"],
  })
    .then((AMap) => {
      const placeSearch = new AMap.PlaceSearch({
        map: mapRef.current,
        city: "全国",
      });

      placeSearch.search(searchValue, (status, result) => {
  console.log("🔍 搜索状态:", status);
  console.log("🔍 搜索结果:", result);

  if (status === "complete" && result?.poiList?.pois?.length > 0) {
    const poi = result.poiList.pois[0];
    console.log("✅ 找到地点:", poi.name, poi.location);
    const latlng = { lat: poi.location.lat, lng: poi.location.lng };
    updateTaskLocation(latlng);
    message.success(`标记移动到: ${poi.name}`);
  } else {
    message.warning("未找到匹配地点");
  }
});
    })
    .catch((err) => console.error("搜索地点失败:", err));
};


  const handleAnalyzeVideo = async () => {
    if (!currentVideoTask?.file) {
      message.error("请先选择视频文件");
      return;
    }

    setAnalyzing(true);
  
    try {
      message.loading("正在分析视频中，这可能需要一些时间...", 0);
    
      const formData = new FormData();
      formData.append("video", currentVideoTask.file);

      const response = await fetch(`${API_BASE_URL}/analyze`, {
        method: "POST",
        body: formData,
      });

      message.destroy();

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`分析失败: ${response.status} - ${errorText}`);
      }

      const result = await response.json();
    
      // 更新项目数据
      const updatedProjects = projects.map((project) => {
        if (project.id === currentProject.id) {
          const updatedTasks = project.videoTasks.map((task) => {
            if (task.id === currentVideoTask.id) {
              return {
                ...task,
                analysisResults: {
                  vehicleCount: result.vehicle_count,
                  framesChecked: result.frames_checked,
                  pieData: [
                    { name: "车辆", value: result.vehicle_count },
                    { name: "其他", value: Math.max(1, result.frames_checked - result.vehicle_count) }
                  ],
                  barData: [{ name: "车辆数量", count: result.vehicle_count }],
                  plateColorData: demoPlateColorData,
                  newEnergyData: demoNewEnergyData,
                  vehicleModelData: demoVehicleModelData,
                  params: { ...analysisParams }
                }
              };
            }
            return task;
          });
          return { ...project, videoTasks: updatedTasks };
        }
        return project;
      });

      setProjects(updatedProjects);
      setCurrentVideoTask({
        ...currentVideoTask,
        analysisResults: {
          vehicleCount: result.vehicle_count,
          framesChecked: result.frames_checked,
          pieData: [
            { name: "车辆", value: result.vehicle_count },
            { name: "其他", value: Math.max(1, result.frames_checked - result.vehicle_count) }
          ],
          barData: [{ name: "车辆数量", count: result.vehicle_count }],
          plateColorData: demoPlateColorData,
          newEnergyData: demoNewEnergyData,
          vehicleModelData: demoVehicleModelData,
          params: { ...analysisParams }
        }
      });
    
      setAnalysisActiveKey(['1']);
      message.success(`分析完成！在 ${result.frames_checked} 帧中检测到 ${result.vehicle_count} 辆车辆`);

    } catch (error) {
      message.destroy();
      console.error("分析错误:", error);
      message.error(`分析失败: ${error.message}`);
    } finally {
      setAnalyzing(false);
    }
  };

  const loginTabs = [
    {
      key: "1",
      label: "微信扫码",
      children: <Button type="primary" block onClick={handleLogin}>扫码登录 (演示)</Button>,
    },
    {
      key: "2",
      label: "手机号登录",
      children: (
        <Form layout="vertical" onFinish={handleLogin}>
          <Form.Item label="手机号" name="phone"><Input /></Form.Item>
          <Form.Item label="验证码" name="code"><Input /></Form.Item>
          <Button type="primary" htmlType="submit" block>登录 (演示)</Button>
        </Form>
      ),
    },
    {
  key: "3",
  label: "邮箱登录",
  children: (
    <Form layout="vertical" onFinish={handleEmailLogin}>
      <Form.Item label="邮箱或手机号" name="identifier" rules={[{ required: true }]}>
        <Input />
      </Form.Item>
      <Form.Item label="密码" name="password" rules={[{ required: true }]}>
        <Input.Password />
      </Form.Item>
      <div style={{ display: "flex", gap: 8 }}>
        <Button type="primary" htmlType="submit" block>登录</Button>
        <Button onClick={() => setShowRegister(true)} block>注册</Button>
      </div>
    </Form>
  )
}

  ];

  const generateMenuItems = () => [
    ...projects.map((project) => ({
      key: project.id,
      icon: <FolderOutlined />,
      label: project.name,
      children: project.videoTasks.map((task) => ({
        key: task.id,
        icon: <FileImageOutlined />,
        label: task.name,
        onClick: () => setCurrentVideoTask(task),
      })),
      onTitleClick: () => { setCurrentProject(project); setCurrentVideoTask(null); },
    })),
    { key: "new-project", icon: <PlusOutlined />, label: "新建项目", onClick: showCreateProject },
  ];

  if (!loggedIn) {
  return (
    <div
      style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        minHeight: "100vh",
        width: "100vw",
      }}
    >
      {contextHolder}
      <Card title="车辆信息智能识别与数据分析平台" style={{ width: 400 }}>
        <Tabs defaultActiveKey="1" items={loginTabs} />
      </Card>

      {/* ✅ 注册表单弹窗放在这里 */}
      <Modal
        title="注册新账户"
        open={showRegister}
        footer={null}
        onCancel={() => setShowRegister(false)}
      >
        <Form layout="vertical" onFinish={handleRegister}>
          <Form.Item label="邮箱" name="email">
            <Input placeholder="可选，邮箱或手机号至少填一项" />
          </Form.Item>
          <Form.Item label="手机号" name="phone">
            <Input />
          </Form.Item>
          <Form.Item
            label="密码"
            name="password"
            rules={[{ required: true, message: "请输入密码" }]}
          >
            <Input.Password />
          </Form.Item>
          <Button type="primary" htmlType="submit" block>
            注册
          </Button>
        </Form>
      </Modal>
    </div>
  );
}


  // ------------------ 演示统计数据 ------------------
  const demoPieData = [
    { name: "SUV", value: 40 },
    { name: "Sedan", value: 30 },
    { name: "Truck", value: 20 },
    { name: "Other", value: 10 },
  ];
  const demoBarData = [
    { name: "Brand A", count: 12 },
    { name: "Brand B", count: 20 },
    { name: "Brand C", count: 8 },
    { name: "Brand D", count: 16 },
  ];
  const demoPlateColorData = [
    { name: "蓝牌", value: 50 },
    { name: "黄牌", value: 20 },
    { name: "白牌", value: 20 },
    { name: "黑牌", value: 10 },
  ];
  const demoNewEnergyData = [
    { name: "新能源", value: 25 },
    { name: "非新能源", value: 75 },
  ];
  const demoVehicleModelData = [
    { name: "Model A", count: 15 },
    { name: "Model B", count: 22 },
    { name: "Model C", count: 10 },
  ];

  return (
    <Layout style={{ minHeight: "100vh", width: "100vw" }}>
      <Header style={{ color: "white", fontSize: 20, padding: "0 24px", position: "sticky", top: 0, zIndex: 1 }}>
  <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
    <div style={{ fontSize: 20, fontWeight: 600 }}>
      车辆信息智能识别与数据分析平台
    </div>

    {/* 右侧按钮：简单退出 */}
    <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
      {/* 若你想要一个带确认的退出：用 Popconfirm（下面注释掉的例子） */}
      {/*
      <Popconfirm
        title="确定要退出登录吗？"
        onConfirm={handleLogout}
        okText="确定"
        cancelText="取消"
      >
        <Button danger>退出登录</Button>
      </Popconfirm>
      */}

      {/* 或者直接退出（简洁） */}
      <Button danger onClick={handleLogout}>退出登录</Button>
    </div>
  </div>
</Header>

      <Layout style={{ flexDirection: "row", flex: 1 }}>
        <Sider width={280} style={{ background: "#001529", overflow: "auto", height: "calc(100vh - 64px)" }}>
          <Menu
            mode="inline"
            selectedKeys={[currentProject?.id?.toString(), currentVideoTask?.id?.toString()]}
            defaultOpenKeys={currentProject ? [currentProject.id.toString()] : []}
            style={{ height: "100%", borderRight: 0 }}
            items={generateMenuItems()}
          />
        </Sider>
        <Content style={{ padding: 24, background: "#fff", overflow: "auto", flex: 1, height: "calc(100vh - 64px)", minWidth: 0 }}>
          {!currentProject && (
            <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "100%" }}>
              <div style={{ textAlign: "center" }}>
                <p>请选择或创建一个项目</p>
                <Button type="primary" onClick={showCreateProject}>创建新项目</Button>
              </div>
            </div>
          )}

          {currentProject && !currentVideoTask && (
            <div style={{ width: "100%" }}>
              <Card title={`项目: ${currentProject.name}`} style={{ marginBottom: 24 }}>
                <Upload
                  fileList={uploadList}
                  onChange={handleUploadChange}
                  beforeUpload={() => false}
                  multiple
                  showUploadList={false}
                  style={{ marginBottom: 24 }}
                >
                  <Button icon={<UploadOutlined />}>上传视频</Button>
                </Upload>

                <Card title="视频任务列表" style={{ marginTop: 16 }}>
                  {getCurrentProjectVideoTasks().length > 0 ? (
                    <List
                      itemLayout="horizontal"
                      dataSource={getCurrentProjectVideoTasks()}
                      renderItem={(task) => (
                        <List.Item
                          actions={[
                            <Button type="link" onClick={() => setCurrentVideoTask(task)}>查看详情</Button>,
                            <Button type="link" danger onClick={() => {
                              const updatedProjects = projects.map(project => {
                                if (project.id === currentProject.id) {
                                  return { ...project, videoTasks: project.videoTasks.filter(t => t.id !== task.id) };
                                }
                                return project;
                              });
                              setProjects(updatedProjects);
                              setCurrentProject(updatedProjects.find(p => p.id === currentProject.id));
                              message.success(`已删除任务: ${task.name}`);
                            }}>删除</Button>
                          ]}
                        >
                          <List.Item.Meta avatar={<Avatar icon={<FileImageOutlined />} />} title={task.name} description={`上传于: ${task.createdAt.toLocaleString()}`} />
                          <div>{task.analysisResults ? <Tag color="green">已分析</Tag> : <Tag color="blue">待分析</Tag>}</div>
                        </List.Item>
                      )}
                    />
                  ) : (
                    <div style={{ textAlign: "center", padding: 20 }}>
                      <p>暂无视频任务</p>
                      <p>请上传视频/影像文件</p>
                    </div>
                  )}
                </Card>
              </Card>
            </div>
          )}

          {currentProject && currentVideoTask && (
            <div style={{ width: "100%" }}>
              <div style={{ marginBottom: 16 }}>
                <Button type="link" onClick={() => setCurrentVideoTask(null)} style={{ padding: 0, marginBottom: 8 }}>&larr; 返回项目</Button>
                <h2>{currentProject.name} / {currentVideoTask.name}</h2>
              </div>

              <Card title="视频预览" style={{ marginBottom: 24, width: "100%" }}>
                {previewUrl ? <video controls style={{ width: "100%", maxHeight: 400, background: "#000" }} src={previewUrl} /> : <p>暂无视频预览</p>}
              </Card>

              <Card title="地理信息" style={{ marginBottom: 24, width: "100%", position: "relative" }}>
                <div style={{ display: "flex", gap: 16, marginBottom: 8 }}>
  <Input
    addonBefore="纬度"
    value={currentVideoTask.location?.lat || ""}
    onChange={(e) =>
      updateTaskLocation({
        lat: parseFloat(e.target.value) || 0,
        lng: currentVideoTask.location?.lng || 0,
      })
    }
  />
  <Input
    addonBefore="经度"
    value={currentVideoTask.location?.lng || ""}
    onChange={(e) =>
      updateTaskLocation({
        lat: currentVideoTask.location?.lat || 0,
        lng: parseFloat(e.target.value) || 0,
      })
    }
  />
  <Input
    placeholder="搜索地点"
    value={searchValue}
    onChange={(e) => setSearchValue(e.target.value)}
  />
  <Button type="primary" onClick={handleSearchPlace}>
    搜索
  </Button>
  <Button
    icon={<AimOutlined />}   // 准星样式
    onClick={() => {
      if (markerRef.current && mapRef.current) {
        const pos = markerRef.current.getPosition();
        mapRef.current.setCenter(pos);
        message.info("地图已居中到标记位置");
      }
    }}
  />
</div>
                <div id="amap-container" style={{ height: 300, border: "1px solid #ddd", borderRadius: 8 }} />
              </Card>

              <Card title="识别参数" style={{ marginTop: 16 }}>
                <div style={{ display: "flex", flexWrap: "wrap", gap: 16 }}>
                  {[
                    { key: "plateNumber", label: "车牌号码" },
                    { key: "vehicleBrand", label: "车辆品牌" },
                    { key: "vehicleType", label: "车辆类型" },
                    { key: "plateColor", label: "车牌颜色" },
                    { key: "vehicleModel", label: "车辆型号" },
                    { key: "vehicleColor", label: "车辆颜色" },
                    { key: "newEnergy", label: "新能源车" }
                  ].map(item => (
                    <Switch
                      key={item.key}
                      checkedChildren={item.label}
                      unCheckedChildren={item.label}
                      checked={analysisParams[item.key]}
                      onChange={(checked) => setAnalysisParams({ ...analysisParams, [item.key]: checked })}
                    />
                  ))}
                </div>
              </Card>

              <Button 
                type="primary" 
  		style={{ marginTop: 16 }} 
  		onClick={handleAnalyzeVideo}
  		loading={analyzing}
  		disabled={analyzing}
	      >
  		{analyzing ? "分析中..." : "开始分析"}
	      </Button>

              {currentVideoTask.analysisResults && (
                <Card title="演示统计图表" style={{ marginTop: 24 }}>
                  <Collapse activeKey={analysisActiveKey} onChange={(key) => setAnalysisActiveKey(key)} expandIcon={({ isActive }) => <CaretRightOutlined rotate={isActive ? 90 : 0} />}>
                    <Panel header="分析结果与数据共享设置" key="1">
                      <Form.Item label="授权共享">
                        <Switch
                          checked={currentVideoTask.shareAllowed || false}
                          onChange={(checked) => {
                            const updatedProjects = projects.map(project => {
                              if (project.id === currentProject.id) {
                                const updatedTasks = project.videoTasks.map(task => {
                                  if (task.id === currentVideoTask.id) {
                                    return { ...task, shareAllowed: checked };
                                  }
                                  return task;
                                });
                                return { ...project, videoTasks: updatedTasks };
                              }
                              return project;
                            });
                            setProjects(updatedProjects);
                            setCurrentVideoTask({ ...currentVideoTask, shareAllowed: checked });
                          }}
                        />
                      </Form.Item>

                      <h4>用户选择的分析参数</h4>
                      <table style={{ width: "100%", borderCollapse: "collapse", marginBottom: 24 }}>
                        <thead>
                          <tr>
                            <th style={{ border: "1px solid #ddd", padding: 8 }}>参数项</th>
                            <th style={{ border: "1px solid #ddd", padding: 8 }}>状态</th>
                          </tr>
                        </thead>
                        <tbody>
                          {Object.entries(currentVideoTask.analysisResults.params || {}).map(([key, value]) => (
                            <tr key={key}>
                              <td style={{ border: "1px solid #ddd", padding: 8 }}>{key}</td>
                              <td style={{ border: "1px solid #ddd", padding: 8 }}>{value ? "开启" : "关闭"}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>

		      {/* 显示真实检测结果 */}
		  <div style={{ marginBottom: 24, padding: 16, background: '#f5f5f5', borderRadius: 8 }}>
  		<h4>📊 检测统计</h4>
  		  <p><strong>检测帧数:</strong> {currentVideoTask.analysisResults.framesChecked}</p>
  		  <p><strong>检测到车辆数:</strong> {currentVideoTask.analysisResults.vehicleCount}</p>
		</div>

		      {/* 车辆数量图表 */}
		<h4>车辆检测统计</h4>
		<ResponsiveContainer width="100%" height={300}>
  		<BarChart data={[{ name: '检测车辆', count: currentVideoTask.analysisResults.vehicleCount }]}>
    		  <XAxis dataKey="name" />
    		  <YAxis />
    		  <Tooltip />
    		  <Bar dataKey="count" fill="#1890ff" />
  		</BarChart>
		</ResponsiveContainer>

		      {/* 其他模拟图表可以保留，但标注为示例 */}
		<div style={{ marginTop: 32 }}>
  		<Alert 
    		message="以下为示例数据" 
    		description="车辆品牌、颜色等详细分析功能正在开发中" 
    		type="info" 
    		showIcon 
 		/>
		</div>
                      {/* 图表和对应表格 */}
                      {[
                        { title: "车辆类型分布", data: currentVideoTask.analysisResults.pieData, type: "pie" },
                        { title: "车辆品牌统计", data: currentVideoTask.analysisResults.barData, type: "bar" },
                        { title: "车牌颜色分布", data: currentVideoTask.analysisResults.plateColorData, type: "pie" },
                        { title: "新能源车比例", data: currentVideoTask.analysisResults.newEnergyData, type: "pie" },
                        { title: "车辆型号统计", data: currentVideoTask.analysisResults.vehicleModelData, type: "bar" },
                      ].map((chart, idx) => (
                        <div key={idx} style={{ marginBottom: 32 }}>
                          <h4>{chart.title}</h4>
                          <ResponsiveContainer width="100%" height={300}>
                            {chart.type === "pie" ? (
                              <PieChart>
                                <Pie data={chart.data} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100} label>
                                  {chart.data.map((entry, index) => (
                                    <Cell key={index} fill={COLORS[index % COLORS.length]} />
                                  ))}
                                </Pie>
                                <Tooltip />
                                <Legend />
                              </PieChart>
                            ) : (
                              <BarChart data={chart.data}>
                                <XAxis dataKey="name" />
                                <YAxis />
                                <Tooltip />
                                <Legend />
                                <Bar dataKey="count" fill="#82ca9d" />
                              </BarChart>
                            )}
                          </ResponsiveContainer>

                          {/* 对应表格 */}
                          <table style={{ width: "100%", borderCollapse: "collapse", marginTop: 8 }}>
                            <thead>
                              <tr>
                                <th style={{ border: "1px solid #ddd", padding: 8 }}>名称</th>
                                <th style={{ border: "1px solid #ddd", padding: 8 }}>{chart.type === "pie" ? "数量/比例" : "数量"}</th>
                              </tr>
                            </thead>
                            <tbody>
                              {chart.data.map((item, i) => (
                                <tr key={i}>
                                  <td style={{ border: "1px solid #ddd", padding: 8 }}>{item.name}</td>
                                  <td style={{ border: "1px solid #ddd", padding: 8 }}>{item.value ?? item.count}</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      ))}

                    </Panel>
                  </Collapse>
                </Card>
              )}
            </div>
          )}

          <Modal title="创建新项目" open={isProjectModalVisible} footer={null} onCancel={() => setIsProjectModalVisible(false)}>
            <Form layout="vertical" onFinish={handleCreateProject}>
              <Form.Item label="项目名称" name="name" rules={[{ required: true, message: "请输入项目名称" }]}>
                <Input />
              </Form.Item>
              <Form.Item>
                <Button type="primary" htmlType="submit">创建</Button>
              </Form.Item>
            </Form>
          </Modal>

        </Content>
      </Layout>
    </Layout>
  );
}

// 初始化数据库
function openDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open("VehicleAppDB", 1);
    request.onupgradeneeded = (event) => {
      const db = event.target.result;
      if (!db.objectStoreNames.contains("videos")) {
        db.createObjectStore("videos", { keyPath: "id" });
      }
    };
    request.onsuccess = () => resolve(request.result);
    request.onerror = (e) => reject(e);
  });
}

// 保存文件（可靠的 Promise 实现）
async function saveVideoToDB(id, file) {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    try {
      const tx = db.transaction("videos", "readwrite");
      const store = tx.objectStore("videos");
      const req = store.put({ id, file });
      req.onsuccess = () => resolve(true);
      req.onerror = (e) => reject(e);
      // 保险：在事务完成时也 resolve（防止某些浏览器不触发 req.onsuccess）
      tx.oncomplete = () => resolve(true);
      tx.onerror = (e) => reject(e);
      tx.onabort = (e) => reject(e);
    } catch (err) {
      reject(err);
    }
  });
}

// 读取文件（可靠的 Promise 实现）
async function getVideoFromDB(id) {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    try {
      const tx = db.transaction("videos", "readonly");
      const store = tx.objectStore("videos");
      const req = store.get(id);
      req.onsuccess = () => resolve(req.result ? req.result.file : null);
      req.onerror = (e) => reject(e);
    } catch (err) {
      reject(err);
    }
  });
}

// 删除文件（可靠）
async function deleteVideoFromDB(id) {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    try {
      const tx = db.transaction("videos", "readwrite");
      const store = tx.objectStore("videos");
      const req = store.delete(id);
      req.onsuccess = () => resolve(true);
      req.onerror = (e) => reject(e);
      tx.oncomplete = () => resolve(true);
      tx.onerror = (e) => reject(e);
      tx.onabort = (e) => reject(e);
    } catch (err) {
      reject(err);
    }
  });
}


export default App;