import wx
from socket import *
import threading

#客户端继承wx.Frame 窗口界面
class HwbClient(wx.Frame):
	def __init__(self,c_name):
		#调用父类的初始化函数
		wx.Frame.__init__(self,None,id=101,title='{}的客户端界面'.format(c_name),
			pos=wx.DefaultPosition,size=(400,470))
		pl=wx.Panel(self) #在窗口中初始化一个面板
		#在面板里放按钮，文本输入框
		box = wx.BoxSizer(wx.VERTICAL) #在盒子里面垂直方向自动排版


		grid1 = wx.FlexGridSizer(wx.HORIZONTAL) #可伸缩的水平网格布局
		#创建两个按钮
		connect_button = wx.Button(pl,size=(200,40),label="连接")
		dis_connect_button = wx.Button(pl,size=(200,40),label="断开")
		grid1.Add(connect_button,1,wx.TOP | wx.LEFT) #连接按钮在左边
		grid1.Add(dis_connect_button,1,wx.TOP | wx.RIGHT) #断开按钮在右边
		box.Add(grid1,1,wx.ALIGN_CENTER) #ALIGN_CENTER 联合居中


		#创建聊天内容的文本框，不能写消息:TE_MULTILINE -->多行 TE_READONLY-->只读
		self.show_chat = wx.TextCtrl(pl,size=(400,250),style=wx.TE_MULTILINE | wx.TE_READONLY)
		box.Add(self.show_chat,1,wx.ALIGN_CENTER)

		#创建聊天的输入文本框，可以写
		self.input_chat = wx.TextCtrl(pl,size=(400,100),style=wx.TE_MULTILINE)
		box.Add(self.input_chat,1,wx.ALIGN_CENTER)

		#最后创建两个按钮，分别是发送和重置
		grid2 = wx.FlexGridSizer(wx.HORIZONTAL) #可伸缩的水平网格布局
		#创建两个按钮
		clear_button = wx.Button(pl,size=(200,40),label="重置")
		send_button = wx.Button(pl,size=(200,40),label="发送")
		grid2.Add(clear_button,1,wx.TOP | wx.LEFT) #连接按钮在左边
		grid2.Add(send_button,1,wx.TOP | wx.RIGHT) #断开按钮在右边
		box.Add(grid2,1,wx.ALIGN_CENTER)


		pl.SetSizer(box) #把盒子放入面板中
		'''以上代码完成了客户端窗口'''

		'''给所有按钮绑定点击事件'''
		self.Bind(wx.EVT_BUTTON,self.Connect_To_Server,connect_button)
		self.Bind(wx.EVT_BUTTON,self.Send_To_Server,send_button)
		self.Bind(wx.EVT_BUTTON,self.Disconnect_To_Server,dis_connect_button)
		self.Bind(wx.EVT_BUTTON,self.Reset,clear_button)

		'''客户端属性'''
		self.name = c_name
		self.isConnected = False #客户端是否已经连上服务器
		self.client_socket = None

	#连接服务器
	def Connect_To_Server(self,event):
		try:
			print("客户端{},开始连接服务器……".format(self.name))
			if not self.isConnected:
				server_host_port = ('172.20.18.109',8888)
				self.client_socket = socket(AF_INET,SOCK_STREAM)
				self.client_socket.connect(server_host_port)
				# 之前规定，客户端连接成功，马上发送名字给服务器
				self.client_socket.send(self.name.encode('UTF-8'))
				client_thread = threading.Thread(target=self.Receive_Data)
				client_thread.daemon = True #客户端UI界面如果关闭，当前守护线程也自动关闭
				self.isConnected = True
				client_thread.start()
		except:
			self.show_chat.AppendText("\n未找到服务器，连接失败\n")

	#接受服务器发送过来的聊天数据
	def Receive_Data(self):
		try:
			while self.isConnected:
				data = self.client_socket.recv(1024).decode('UTF-8')
				if data == "服务器已关闭":
					self.isConnected = False
				# 从服务器接受到的数据，需要显示
				self.show_chat.AppendText('{}\n'.format(data))
		except:
			return

	def Send_To_Server(self,event):
	#客户端发送消息到聊天室
		if self.isConnected:
			information = self.input_chat.GetValue()
			if information != '':
				self.client_socket.send(information.encode('UTF-8'))
				#若输入框中的数据已经发送，输入框清空
				self.input_chat.SetValue('')


	#客户端离开聊天室
	def Disconnect_To_Server(self,event):
		if self.isConnected:
			self.client_socket.send('A^disconnect^B'.encode('UTF-8'))
			self.isConnected = False
			#客户端主线程也要关闭
			self.client_socket.close()

	#客户端输入框的信息重置
	def Reset(self,event):
		self.input_chat.Clear()

if __name__ == '__main__':
	app=wx.App()
	name = input("请输入客户端名字：")
	HwbClient(name).Show()
	app.MainLoop() #循环刷新显示