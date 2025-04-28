def GetInt(value):
	try:
		temp = float(value)
		if temp % 1 == 0:
			return int(temp)
		else:
			return None
	except:
		return None