package br.com.lampdata.pitukontrol.flex.poc
{
	[Bindable]
	public class ABC {
		public function ABC(n : int) {
			a = "a"+n;
			b = "b"+n;
			c = "c"+n;
		}
		
		public var a : String;
		public var b : String;
		public var c : String;
	}
}