export function InitData () {
  return {
    logged: false,
    drawer: false,
    // server: 'https://so.alexhal.me',
    nextPbkdf2: '',
    user: {},
    solst: { dlists: [], slists: [] }
  }
}

export function PrivMap () {
  return {
    0: { 0: [], 1: [], 2: [], 3: [], 4: [] },
    1: { 0: [0, 1, 2, 3, 4], 1: [], 2: [0, 1, 2, 3, 4], 3: [0, 1, 2, 3, 4], 4: [0, 1, 2, 3, 4] },
    2: { 0: [0, 2, 3, 4], 1: [], 2: [], 3: [0, 2, 3, 4], 4: [0, 2, 3, 4] },
    3: { 0: [], 1: [], 2: [], 3: [], 4: [] },
    4: { 0: [], 1: [], 2: [], 3: [], 4: [] }
  }
}

export function ModalText () {
  return {
    cookie: {
      icon: 'cloud_off',
      title: 'You were disconnected',
      text: 'Please input password to continue',
      btn: [['logout', ''], ['login', '']],
      input0: true,
      input12: false
    },
    first: {
      icon: 'person_add',
      title: 'Welcome to Signout',
      text: 'Please input the password provided by email as current password and choose a new password',
      btn: [['cancel', ''], ['login', '']],
      input0: true,
      input12: true
    },
    change: {
      icon: 'password',
      title: 'Password change required',
      btn: [['cancel', ''], ['reset', '']],
      text: '',
      input0: true,
      input12: true
    },
    reset: {
      icon: 'report',
      title: 'Password reset requested',
      text: 'A password reset was requested. If you remember your password, hit Abort password reset. Otherwise, input new password and hit Reset. As this service is server-side zero-knowledge encrypted, you will lose access to all your lists and other list users might gain privileges in order for lists to be managed. This is a desctrutive operation.',
      btn: [['cancel', ''], ['reset', 'bg-red-6 text-white'], ['abord password reset', '']],
      input0: true,
      input12: true
    }
  }
}
