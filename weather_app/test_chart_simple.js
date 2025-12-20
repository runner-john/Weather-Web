// 简单测试图表绘制逻辑

// 模拟必要的DOM元素
const mockCanvas = {
    getContext: function(type) {
        if (type === '2d') {
            return {
                clearRect: function() {},
                fillRect: function() {},
                strokeRect: function() {},
                beginPath: function() {},
                moveTo: function() {},
                lineTo: function() {},
                closePath: function() {},
                stroke: function() {},
                fill: function() {},
                arc: function() {},
                rect: function() {},
                fillText: function() {},
                strokeText: function() {},
                measureText: function() { return { width: 0 }; },
                createLinearGradient: function() { return {}; },
                createPattern: function() { return {}; },
                createRadialGradient: function() { return {}; },
                drawImage: function() {},
                save: function() {},
                restore: function() {},
                translate: function() {},
                rotate: function() {},
                scale: function() {},
                transform: function() {},
                setTransform: function() {},
                clip: function() {},
                isPointInPath: function() { return false; },
                isPointInStroke: function() { return false; },
                drawFocusRing: function() {},
                scrollPathIntoView: function() {},
                fillStyle: '',
                strokeStyle: '',
                lineWidth: 1,
                lineCap: 'butt',
                lineJoin: 'miter',
                miterLimit: 10,
                lineDashOffset: 0,
                shadowColor: 'transparent',
                shadowBlur: 0,
                shadowOffsetX: 0,
                shadowOffsetY: 0,
                globalAlpha: 1,
                globalCompositeOperation: 'source-over',
                font: '10px sans-serif',
                textAlign: 'start',
                textBaseline: 'alphabetic',
                direction: 'ltr',
                imageSmoothingEnabled: true,
                imageSmoothingQuality: 'low'
            };
        }
        return null;
    }
};

// 模拟window对象
const window = {
    temperatureChart: null,
    addEventListener: function() {}
};

// 模拟document对象
const document = {
    getElementById: function(id) {
        if (id === 'temperatureChart') {
            return mockCanvas;
        }
        if (id === 'chartContainer') {
            return {
                style: { display: 'block' },
                querySelector: function() { return null; }
            };
        }
        return null;
    },
    createElement: function() { return mockCanvas; }
};

// 模拟Chart.js
const Chart = {
    version: '4.4.0',
    prototype: {
        destroy: function() {},
        update: function() {},
        resize: function() {}
    }
};

// 简单测试数据
const testCities = ['北京', '上海', '广州', '深圳', '杭州'];
const testTemperatures = [1.0, 5.0, 15.0, 16.0, 8.0];

// 测试函数定义
function showStaticTemperatureTable(cities, temperatures) {
    console.log('显示静态温度表格:', cities, temperatures);
}

// 测试图表绘制函数的核心逻辑
function testChartLogic() {
    console.log('开始测试图表绘制逻辑');
    
    try {
        // 测试数据处理
        const processedTemperatures = testTemperatures.map((temp, index) => {
            if (temp === null || temp === undefined) {
                console.warn(`城市 ${testCities[index]} 温度数据为null或undefined`);
                return 0;
            }
            
            // 如果温度是字符串，尝试解析
            if (typeof temp === 'string') {
                // 移除温度符号和空格
                const cleanTemp = temp.replace(/[°C℃ ]/g, '');
                const parsedTemp = parseFloat(cleanTemp);
                if (isNaN(parsedTemp)) {
                    console.warn(`城市 ${testCities[index]} 温度数据格式错误: ${temp}`);
                    return 0;
                }
                return parsedTemp;
            }
            
            // 如果温度是数字，直接使用
            if (typeof temp === 'number') {
                if (isNaN(temp)) {
                    console.warn(`城市 ${testCities[index]} 温度数据为NaN`);
                    return 0;
                }
                return temp;
            }
            
            // 其他情况返回0
            console.warn(`城市 ${testCities[index]} 温度数据类型错误: ${typeof temp}`);
            return 0;
        });
        
        console.log('✅ 数据处理成功:', processedTemperatures);
        
        // 测试温度范围计算
        const validTemperatures = processedTemperatures.filter(temp => temp !== 0);
        const minTemp = validTemperatures.length > 0 ? Math.floor(Math.min(...validTemperatures) - 5) : 0;
        const maxTemp = validTemperatures.length > 0 ? Math.ceil(Math.max(...validTemperatures) + 5) : 30;
        
        console.log('✅ 温度范围计算成功:', minTemp, '到', maxTemp);
        
        // 测试图表配置
        const chartConfig = {
            type: 'bar',
            data: {
                labels: testCities,
                datasets: [{
                    label: '当前温度 (°C)',
                    data: processedTemperatures,
                    backgroundColor: 'rgba(54, 162, 235, 0.8)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1,
                    borderRadius: 3,
                    barThickness: 30,
                    maxBarThickness: 50
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: false,
                        min: minTemp,
                        max: maxTemp,
                        title: {
                            display: true,
                            text: '温度 (°C)',
                            font: {
                                size: 14,
                                weight: 'normal'
                            }
                        },
                        ticks: {
                            callback: function(value) {
                                return value + '°C';
                            },
                            autoSkip: true,
                            maxTicksLimit: 8
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: '城市',
                            font: {
                                size: 14,
                                weight: 'normal'
                            }
                        },
                        ticks: {
                            maxRotation: 45,
                            minRotation: 30
                        },
                        grid: {
                            display: false
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: '热门城市温度实时对比',
                        font: {
                            size: 16,
                            weight: 'bold'
                        },
                        padding: {
                            top: 5,
                            bottom: 20
                        }
                    },
                    tooltip: {
                        enabled: true,
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        padding: 8
                    },
                    legend: {
                        display: true,
                        position: 'top'
                    }
                },
                animation: {
                    duration: 0
                },
                layout: {
                    padding: 10
                }
            }
        };
        
        console.log('✅ 图表配置创建成功');
        
        console.log('✅ 所有测试通过！');
        
    } catch (error) {
        console.error('❌ 测试失败:', error);
        console.error('错误堆栈:', error.stack);
    }
}

// 运行测试
testChartLogic();
