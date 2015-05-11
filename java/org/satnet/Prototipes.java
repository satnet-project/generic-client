package org.satnet;

import com.twistedmatrix.amp.LocalCommand;

/**
 * This class contains all the prototipes of the commands that can be executed
 * either on the server or on the client side. Each command is divided into two
 * public (and static for readability) classes containing the params and the
 * response that generate those params.
 * 	 
 * All command classes and all its variables must be public.
 * 
 * @author xabicrespog@gmail.com
 *
 */
public class Prototipes {
	// COMMANDS EXECUTED ON THE SERVER SIDE
	// --------------------------------------------------
	/**
	 * Login command responses
	 */
	public static class LoginResp {
		public boolean bAuthenticated;

		public boolean getResponse() {
			return bAuthenticated;
		}
	}

	/**
	 * Login command parameters
	 */
	public static class LoginParams {
		public String sUsername;
		public String sPassword;

		public LoginParams(String username, String password) {
			this.sUsername = username;
			this.sPassword = password;
		}
	}
	
	/**
	 * StartRemote command responses
	 */
	public static class StartRemoteResp {
		public Integer iResult;

		public int getResponse() {
			return iResult;
		}
	}

	/**
	 * StartRemote command parameters
	 */
	public static class StartRemoteParams {
		public Integer iSlotId;		

		public StartRemoteParams(int slotId) {
			this.iSlotId = slotId;
		}
	}
	
	/**
	 * EndRemote command responses. This command has no response.
	 */
	public static class EndRemoteResp {
	}

	/**
	 * EndRemote command parameters. This command does not need any parameter.
	 */
	public static class EndRemoteParams {
	}
	
	/**
	 * SendMsg command responses
	 */
	public static class SendMsgResp {
		public boolean bResult;

		public boolean getResponse() {
			return bResult;
		}
	}

	/**
	 * SendMsg command parameters
	 */
	public static class SendMsgParams {
		public String sMsg;
		public int iTimeStamp;

		public SendMsgParams(String msg, int timeStamp) {
			this.sMsg = msg;
			this.iTimeStamp = timeStamp;
		}
	}

	// COMMANDS EXECUTED ON THE CLIENT SIDE
	// --------------------------------------------------
	/**
	 * NotifyEvent command responses
	 */
	public static class NotifyEventResp {
		// Possible events
		public final static int REMOTE_DISCONNECTED = -1;
		public final static int SLOT_END = -2;
		public final static int END_REMOTE = -3;
		public final static int REMOTE_CONNECTED = -4;
		
		public Integer iEvent;
		public String sDetails;

		public String getEvent() {
			switch (iEvent) {
			case REMOTE_DISCONNECTED:
				return "Remote disconnected";
			case SLOT_END:
				return "Slot end";
			case END_REMOTE:
				return "End remote";
			case REMOTE_CONNECTED:
				return "Remote connected";
			default:
				return "Unknown event received";
			}
		}

		public String getDetails() {
			return sDetails;
		}
	}

	/**
	 * NotifyEvents command
	 */
	public static class NotifyEventCommand extends LocalCommand {
		public Integer iEvent;
		public String sDetails;

		public NotifyEventCommand() {
			super("NotifyEvent", new String[] { "iEvent", "sDetails" });
		}
	}
	
	/**
	 * NotifyEvent command responses
	 */
	public static class NotifyMsgResp {
		public String sMsg;

		public String getMessage() {
			return sMsg;
		}
	}

	/**
	 * NotifyEvents command
	 */
	public static class NotifyMsgCommand extends LocalCommand {
		public String sMsg;

		public NotifyMsgCommand() {
			super("NotifyMsg", new String[] { "sMsg" });
		}
	}	
	
}