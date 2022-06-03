# 拟音歌词注音处理工具

一些用于处理古汉语拟音歌词注音及其他相关功能的简单程序。

`ngixqlrc`来自Polyhedron式中古拼音的`ngix qim`（拟音）和歌词文件后缀`.lrc`。

## 安装

本程序需要使用Python 3.9或以上版本，使用完整功能需要安装`lxml` `imgkit` 第三方库，还需要安装[wkhtmltopdf](https://wkhtmltopdf.org/)并将其添加到`PATH`环境变量中。

因为很可能需要修改源代码来改配置，故建议使用开发者模式安装，在当前目录下执行：

```
python -m pip install -e .
```

## 使用

目前皆为命令行脚本，请在安装完成后，在命令行使用`-m`选项来执行各模块功能，例如

```
python -m ngixqlrc.lrc2srt 人间入画.lrc
```

目前有下列模块：

- `lrc2srt` 将`lrc`歌词文件转换为`srt`字幕文件
- `lrc2bcc` 将`lrc`歌词文件转换为`bcc`文件，即B站的字幕描述文件
- `make_lyric_html` 生成（适合打印的）歌词文本与注音逐字对应的html文档 （详见后文）
- `make_subtitle_serial` 生成歌词文本与注音逐字对应的、带有时间轴的、字幕序列（适用于Premiere软件）（详见后文）

## 文件与示例

示例位于`example`目录下。这里采用歌曲《人间入画》的歌词及其中古拼音注音作为示例。

> 原唱：司夏/河图  https://music.163.com/#/song?id=29811165
>
> 这里使用的注音为Polyhedron式中古拼音，资料来自[韵典网](https://ytenx.org/)。事实上用其他拼音或者音标等也可以，只需要满足各字注音之间以空白字符分隔即可。

主要涉及两个文件：

- 汉字歌词文件，这里是`人间入画-汉字-对照版.lrc`。需要有LRC格式的时间轴标记；其中每一行以**字符**为单位拆分。文本中的`|`符号表示换行符，在`make_lyric_html`模块中被忽略，在`make_subtitle_html`文件中作为换行的标记。
- 注音歌词文件，这里是`人间入画-中古-对照版.txt`。只需要有文本即可，不需要时间轴。其中每一行以**单词**为单位拆分，每一拆分单位与汉字歌词中的每一字符对应。拆分以空白字符进行。其中，大写字母在`make_lyric_html`模块中将被转换为红色的小写字母。

注意以上两个文件需要**逐行一一对应**（包括空行）。应尽量避免在以上文件中包含空行。

### 转换为文档

打开命令行窗口，切换到以上两文件所在目录，输入

```
python -m ngixqlrc.make_lyric_html 人间入画-中古-对照版.txt 人间入画-汉字-对照版.lrc 人间入画歌词对照.html 人间入画-中古-lower.txt
```

其中最后一个参数可选，如果给出，则输出为纯小写版本的歌词文件。

输出的html文档为`人间入画歌词对照.html`，可用浏览器查看、打印。

### 转换为视频字幕

打开命令行窗口，切换到以上两文件所在目录，输入

```
python -m ngixqlrc.make_subtitle_serial 人间入画-中古-对照版.txt 人间入画-汉字-对照版.lrc serial_out
```

其中`serial_out`为输出的**目录**名。程序正常结束时，将在该目录内得到一系列字幕的`PNG`图片文件和一个描述序列的`xml`文件。将该`xml`文件导入Premiere软件中，即可作为**序列**使用，添加到其他视频序列中。可进一步调整位置。输出图片的大小可由命令行参数指定。

注：这里PNG图片的生成是先生成html，再用`imgkit`（实质上是调用`wkhtmltoimage`）转换成图片的。若要修改字体、字体大小、阴影等，可以修改写入的css内容。

使用本程序生成的样例视频：（待更新）

## 关于

本项目Github链接：https://github.com/CDK6182CHR/ngixqlrc

GPLv3

作者：萧迩珀   

- 邮箱：mxy0268@qq.com
- B站：https://space.bilibili.com/179545382

## Acknowledgement

感谢[Arctime](https://arctime.org/index.html)软件，对本项目部分功能有所启发。
