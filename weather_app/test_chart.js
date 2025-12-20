// 测试图表绘制逻辑的语法错误
const fs = require('fs');
const path = require('path');

// 读取HTML文件
const htmlPath = path.join(__dirname, 'app', 'templates', 'index.html');
const htmlContent = fs.readFileSync(htmlPath, 'utf8');

// 提取drawTemperatureChart函数
const chartFunctionRegex = /function drawTemperatureChart\([\s\S]*?\}\s*\}\s*\}\s*\n\s*\)/;
const match = htmlContent.match(chartFunctionRegex);

if (match) {
    const chartFunction = match[0];
    
    // 检查函数语法
    try {
        // 尝试解析为JavaScript代码
        new Function(chartFunction);
        console.log('✅ drawTemperatureChart函数语法正确');
        
        // 检查关键变量和函数是否存在
        const keyElements = [
            'Chart',
            'canvas.getContext',
            'window.temperatureChart',
            'showStaticTemperatureTable'
        ];
        
        keyElements.forEach(element => {
            if (chartFunction.includes(element)) {
                console.log(`✅ 包含关键元素: ${element}`);
            } else {
                console.log(`⚠️  缺少关键元素: ${element}`);
            }
        });
        
    } catch (error) {
        console.error('❌ drawTemperatureChart函数语法错误:', error);
    }
} else {
    console.error('❌ 无法找到drawTemperatureChart函数');
}
