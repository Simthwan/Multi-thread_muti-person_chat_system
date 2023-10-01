import wx
from socket import *
import threading
import time

class HwbServer(wx.Frame):

	def __init__(self):
		'''创建窗口'''
		wx.Frame.__init__(self,None,id=102,title='HWB的服务器界面',
		pos=wx.DefaultPosition,size=(400,470))
		pl=wx.Panel(self) #在窗口中初始化一个面板
		#在面板里放按钮，文本输入框
		box = wx.BoxSizer(wx.VERTICAL) #在盒子里面垂直方向自动排版


		grid1 = wx.FlexGridSizer(wx.HORIZONTAL) #可伸缩的水平网格布局
		#创建两个按钮
		start_server_button = wx.Button(pl,size=(133,40),label="启动")
		record_save_button = wx.Button(pl,size=(133,40),label="聊天记录保存")
		stop_server_button = wx.Button(pl,size=(133,40),label="停止")
		grid1.Add(start_server_button,1,wx.TOP)
		grid1.Add(record_save_button,1,wx.TOP)
		grid1.Add(stop_server_button,1,wx.TOP)
		box.Add(grid1,1,wx.ALIGN_CENTER) #ALIGN_CENTER 联合居中

		#创建只读的文本框，显示聊天记录
		self.show_chat = wx.TextCtrl(pl,size=(400,400),style=wx.TE_MULTILINE | wx.TE_READONLY)
		box.Add(self.show_chat,1,wx.ALIGN_CENTER)

		pl.SetSizer(box)
		'''以上窗口创建代码结束'''


		'''服务器准备执行的一些属性'''
		self.isOn = False #服务器没有启动
		self.host_port=('172.20.18.109',8888) #服务器绑定的地址和端口号
		self.server_socket = None #TCP协议的服务器端套接字
		self.session_thread = None
		self.session_thread_map={} #存放所有的服务器会话线程,key=客户端名字，value=服务器线程

		'''给所有的按钮绑定相应的动作'''
		self.Bind(wx.EVT_BUTTON,self.Start_Server,start_server_button) #给启动按钮绑定一个事件，事件触发自动调用一个函数
		self.Bind(wx.EVT_BUTTON,self.Save_Record,record_save_button)
		self.Bind(wx.EVT_BUTTON,self.Stop_Server,stop_server_button)

	#服务器开始启动的函数
	def Start_Server(self,event):
		self.server_socket = socket(AF_INET,SOCK_STREAM) #TCP协议的服务器端套接字
		self.server_socket.setsockopt(SOL_SOCKET,SO_REUSEADDR,1) #端口复用
		self.server_socket.bind(self.host_port)
		self.server_socket.listen(5) #服务器监听数量
		print('服务器开始启动')
		if not self.isOn:
			#启动服务器的主线程
			self.isOn = True
			main_thread = threading.Thread(target=self.Do_Work)
			main_thread.daemon = True #设置为守护线程
			main_thread.start()

	#服务器运行之后的函数
	def Do_Work(self):
		print("服务器开始工作")
		try:
			while self.isOn:
				session_socket,client_address = self.server_socket.accept()
				#服务器首先接受客户端发过来的第一天消息，规定第一条消息为客户端的名字
				username = session_socket.recv(1024).decode('UTF-8') #接受客户端的名字
				#创建一个会话线程
				self.session_thread = Session_Thread(session_socket,username,self)
				self.session_thread_map[username] = self.session_thread
				self.session_thread.start()
				#表示有客户端进入聊天室
				self.Show_Information_and_Send_Client("服务器通知","欢迎{}进入聊天室！".format(username),
					time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))
		except:
			self.show_chat.AppendText('\n服务器已停止\n')


	#在文本中显示聊天信息，同时发送消息给所有的客户端 source:信息源 data:信息
	def Show_Information_and_Send_Client(self,source,data,data_time):
		send_data = '{}:{}\n时间:{}\n'.format(source,data,data_time)
		#在服务器文本框显示信息
		self.show_chat.AppendText('------------------------------------\n{}'.format(send_data))
		for client in self.session_thread_map.values():
			if(client.isOn): #当前客户端是运行状态
				client.user_socket.send(send_data.encode('UTF-8'))

	#服务器保存聊天记录
	def Save_Record(self,event):
		record = self.show_chat.GetValue()
		with open("record.log",'a') as f:
			f.write(record)

	#关闭服务器
	def Stop_Server(self,event):
		self.isOn = False
		for client in self.session_thread_map.values():
			if client.isOn:
				client.user_socket.send('服务器已关闭'.encode('UTF-8'))
			client.isOn = False
			client.user_socket.close()
		self.server_socket.close()


#服务器端会话线程的类
class Session_Thread(threading.Thread):
	def __init__(self,user_socket,username,server):
		threading.Thread.__init__(self)
		self.user_socket = user_socket
		self.username = username
		self.server = server
		self.isOn = True

	def run(self): #会话线程的运行
		print('客户端{},已经和客户端连接成功，服务器启动一个会话线程'.format(self.username))
		try:
			while self.isOn:
				data = self.user_socket.recv(1024).decode('UTF-8') #接受客户端的聊天信息
				if data == 'A^disconnect^B': #如果客户端点击断开按钮，先发一条消息给服务器，消息内容规定为：A^disconnect^B
					self.isOn = False
					#有用户离开，需要在聊天室通知其他人
					self.server.Show_Information_and_Send_Client("服务器通知","{}离开聊天室！".format(self.username),
					time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))
				else:
					#其他聊天信息，我们应该显示给所有客户端，包括服务器
					self.server.Show_Information_and_Send_Client(self.username,data,
						time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))
		except:
			return

if __name__ == '__main__':
	app = wx.App()
	HwbServer().Show()
	app.MainLoop() #循环刷新显示